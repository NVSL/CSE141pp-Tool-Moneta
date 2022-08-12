#include <iostream>
#include <sstream>
#include <fcntl.h>
#include <unistd.h>
#include <fstream>
#include <iomanip>
#include <string.h>
#include <utility>
#include <vector>
#include <list>
#include <set>
#include <unordered_set>
#include <unordered_map>
#include <algorithm>
#include <ctype.h>
#include <sys/stat.h> // mkdir
#include "moneta_trace.hpp"
#include "pin.H"   // Pin
#include<cassert>

VOID Instruction(INS ins, VOID *v);
VOID Trace(TRACE trace, VOID *v);

// Pin comes with some old standard libraries.
namespace pintool {
	template <typename V>
	using unordered_set = std::unordered_set<V>;

	template <typename K, typename V>
	using unordered_map = std::unordered_map<K, V>;
}

// Debug vars
constexpr bool DEBUG {0};
constexpr bool EXTRA_DEBUG {0};
constexpr bool INPUT_DEBUG {1};
constexpr bool CACHE_DEBUG {0};

static ADDRINT inst_count = 0;
static int read_insts = 0;
// Cache debug
static int cache_writes {0};
static int comp_misses  {0};
static int cap_misses   {0};
constexpr int SkipRate  {10000};

// Constant Vars for User input
constexpr ADDRINT DefaultMaximumLines   {100000000};
constexpr ADDRINT NumberCacheEntries    {4096};
constexpr ADDRINT DefaultCacheLineSize  {64};
const std::string DefaultOutputPath     {"."};
const std::string DefaultStartFunction  {"__libc_start_main"};
constexpr ADDRINT LIMIT {0};

// Output file formatting
const std::string TraceSuffix    {".mtrace"};
const std::string TagFileSuffix  {".tags"}; //csv
const std::string StatsFileSuffix  {".stats"}; //csv
const std::string MetaFileSuffix {".meta"}; //txt

// User-initialized
static UINT64 max_lines  {DefaultMaximumLines};
static UINT64 cache_size {NumberCacheEntries};
static UINT64 cache_line {DefaultCacheLineSize};
static std::string start_function;
static std::string output_trace_path;
static std::string output_tagfile_path;
static std::string full_output_trace_path;
//static std::string output_metadata_path;

// Macros to track
const std::string DUMP_START {"TAG_START"};
const std::string TAG_GROW {"TAG_GROW"};
const std::string NEW_TRACE {"M_NEW_TRACE"};
const std::string DUMP_STOP  {"TAG_STOP"};
const std::string FLUSH_CACHE  {"FLUSH_CACHE"};
const std::string M_START_TRACE  {"M_START_TRACE"};
const std::string GET_THREAD_ID  {"GET_THREAD_ID"};
const std::string M_STOP_TRACE  {"M_STOP_TRACE"};

UINT64 SkipMemOps = 10000000000000000ull;
bool TaggedOnly = false;



static UINT64 curr_traced_lines {0}; // Increment for every write trace for memory accesses.  Reset when opening a new file.
static UINT64 total_traced_lines {0}; // Increment for every write to trace for memory accesses
static UINT64 all_lines {0}; // Increment for every write to trace for memory accesses

// Increment id for every new tag
static int curr_id {0};

class PINMutexGuard {
	PIN_MUTEX &mutex;
public:
	PINMutexGuard(PIN_MUTEX &m) : mutex(m) {
		PIN_LockClient(); // This is not the right way to do
				  // this, but using our own mutex
				  // leads to hangs with multithreaded
				  // programs.  I'm not sure why.  THe
				  // client lock is recursive, while
				  // the mutex is not.  That may have
				  // something to do with it.
		//PIN_MutexLock(&mutex);
	}
	~PINMutexGuard() {
		PIN_UnlockClient();
		//PIN_MutexUnlock(&mutex);
	}
	
};

#define BE_THREAD_SAFE() PINMutexGuard _guard(the_big_lock)

struct TagData;

struct Tag {
	const TagData* parent;
	const int id;
	bool active {true};
	std::pair<UINT64, UINT64> x_range;
	std::pair<ADDRINT, ADDRINT> addr_range {ULLONG_MAX, 0};
	bool is_thread;
	THREADID thread_id;
	UINT64 access_count;
	
	Tag(TagData* td, int id, bool is_thread, THREADID thread_id, int access ) :
		parent {td},
		id {id},
		x_range {access, access},
		is_thread(is_thread),
		thread_id(thread_id),
		access_count(0)
		{}

	void reset_for_new_file() { // for a new file, everything remains the same except the access number.
		x_range.first = 0;
		x_range.second = 0;
	}
	
	void update(ADDRINT addr, int access) {
		access_count++;
		addr_range.first = std::min(addr_range.first, addr);
		addr_range.second = std::max(addr_range.second, addr);
		x_range.second = access;
	}
};

struct TagData {
	const int id;
	const std::string tag_name;
	std::pair<ADDRINT, ADDRINT> addr_range;
	bool is_thread;
	THREADID thread_id;
	std::vector<Tag*> tags;
  
	TagData(std::string tag_name, ADDRINT low, ADDRINT hi, bool is_thread, THREADID thread_id = 0) : 
		id(curr_id++),
		tag_name {tag_name},
		addr_range({low, hi}),
		is_thread(is_thread),
		thread_id(thread_id)
		{
			this->create_new_tag();
		}

	void create_new_tag() {
		tags.push_back(new Tag(this, tags.size(), is_thread, thread_id, curr_traced_lines));
	}

	void  reset_for_new_file() {
		for (Tag* t : tags) {
			t->reset_for_new_file();
		}
	}
	
	bool update(ADDRINT addr, int access) {
		bool updated {0};
		for (Tag* t : tags) {
			if (t->active) {
				t->update(addr, access);
				updated = true;
			}
		}
		return updated;
	}
	// Default destructor
	~TagData() {
		for (Tag* t : tags) {
			delete t;
		}
	}
};

// Only the id is output to out_file.
typedef std::pair<ADDRINT, ADDRINT> AddressRange; 

pintool::unordered_map<std::string, TagData*> all_tags;


bool reached_start {0};


std::unordered_map<THREADID, TagData *> thread_ids;


/*
 * Write a trace 
 */
class TraceWriter {

	int mem_file;
public:
	TraceWriter(std::string filename) {
		std::cerr << filename << "\n";
		mem_file = open(filename.c_str(), O_WRONLY|O_TRUNC|O_CREAT);
		assert(mem_file != -1);
	}

	~TraceWriter() {
		close(mem_file);
	}

	int write_data_mem(ADDRINT address, int access, THREADID threadid) {

		struct trace_entry entry;
		entry.address = address;
		entry.acc = access;
		entry.threadid = threadid;
		write(mem_file, &entry, sizeof(trace_entry));
		return 0;
	}
};

TraceWriter * trace_writer; // One for this pintool

struct cache_hash { // Could improve on this hash function
	inline std::size_t operator()(const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k) const {
		return (uint64_t)k.first;
	}
};

struct cache_equal {
public:
	inline bool operator()(const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k1, const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k2) const {
 
		if (k1.first == k2.first) {
			return true;
		}
		return false;
	}
};


/*struct cache_compare { // Need this to use set
  inline bool operator() (const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k1, const std::pair<ADDRINT, std::list<ADDRINT>::iterator> & k2) const {
  return k1.first < k2.first;
  }
  };*/


// Stores all info for cache with pointers to where it is in list
std::unordered_map<ADDRINT, std::list<ADDRINT>::const_iterator> accesses;
std::unordered_set<ADDRINT> all_accesses;
PIN_MUTEX the_big_lock;

//std::set<std::pair<ADDRINT, std::list<ADDRINT>::iterator>, cache_compare> accesses; // Try set to see if it's faster than unordered_set
std::list<ADDRINT> inorder_acc; // Everything in cache right now
UINT64 hits = 0;
UINT64 misses = 0;

// Increase the file write buffer to speed up i/o
const unsigned long long BUF_SIZE = 4ULL * 8ULL* 1024ULL * 1024ULL;
static char * buffer1 = new char[BUF_SIZE];
static char * buffer2 = new char[BUF_SIZE];
static char * buffer3 = new char[BUF_SIZE];

// Command line options for pintool
KNOB<std::string> KnobStartFunctionLong(KNOB_MODE_WRITEONCE, "pintool",
					"start", "", "specify name of function to start tracing at");

KNOB<std::string> KnobStartFunction(KNOB_MODE_WRITEONCE, "pintool",
				    "s", "", "specify name of function to start tracing at");

KNOB<std::string> KnobOutputFileLong(KNOB_MODE_WRITEONCE, "pintool",
				     "name", "", "specify name of output trace");

KNOB<UINT64> KnobSkipMemOps(KNOB_MODE_WRITEONCE, "pintool",
			    "skip", "0", "How many memops to skip");

KNOB<std::string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
				 "n", "default", "specify name of output trace");

KNOB<UINT64> KnobMaxOutputLong(KNOB_MODE_WRITEONCE, "pintool",
			       "output_lines", "", "specify max lines of output");


KNOB<UINT64> KnobMaxOutput(KNOB_MODE_WRITEONCE, "pintool",
			   "ol", "10000000", "specify max lines of output");

UINT64 file_count = 0;
KNOB<UINT64> KnobFileCount(KNOB_MODE_WRITEONCE, "pintool",
			   "file_count", "1", "How many trace files to generate");

KNOB<UINT64> KnobCacheSizeLong(KNOB_MODE_WRITEONCE, "pintool",
			       "cache_lines", "", "specify # of lines in L1 cache");

KNOB<UINT64> KnobCacheSize(KNOB_MODE_WRITEONCE, "pintool",
			   "c", "4096", "specify # of lines in L1 cache");

KNOB<UINT64> KnobCacheLineSizeLong(KNOB_MODE_WRITEONCE, "pintool",
				   "block", "", "specify block size in bytes");

KNOB<UINT64> KnobCacheLineSize(KNOB_MODE_WRITEONCE, "pintool",
			       "b", "64", "specify block size in bytes");

KNOB<bool> KnobFlushCacheOnNewFile(KNOB_MODE_WRITEONCE, "pintool",
				   "flush-cache-on-new-file", "false", "Flush the cache when you open a new file?");

KNOB<bool> KnobOnlyTaggedAccesses(KNOB_MODE_WRITEONCE, "pintool",
				  "tagged-only", "false", "Only record tagged accesses");

void exit_early(int v) {
	PIN_MutexUnlock(&the_big_lock);
	PIN_ExitApplication(v);
}
VOID flush_cache() {
	if (CACHE_DEBUG) {
		std::cerr << "Flushing cache\n";
	}
	inorder_acc.clear();
	all_accesses.clear();
	accesses.clear();
	hits = 0;
	misses = 0;
}

VOID flush_cache_user() {
	BE_THREAD_SAFE();
	flush_cache();
}


void reset_tags_for_new_file() {
	for (auto& tag_iter : all_tags) {
		tag_iter.second->reset_for_new_file();
	}
}

void write_tags_and_clear(bool clear_tags) {
	std::vector<Tag*> tags;
	for (auto& tag_iter : all_tags) {
		TagData* td = tag_iter.second;
		tags.reserve(tags.size() + distance(td->tags.begin(), td->tags.end()));
		tags.insert(tags.end(), td->tags.begin(), td->tags.end());
	}
	std::sort(tags.begin(), tags.end(), 
		  []( Tag* left,  Tag* right) {
			  return left->x_range.first < right->x_range.first;
		  });

	std::ofstream tag_file (output_tagfile_path);
	tag_file << "Tag_Name,Tag_Type,Thread_ID,Low_Address,High_Address,First_Access,Last_Access,Access_Count\n"; // Header row
	for (Tag* t : tags) {
		tag_file << t->parent->tag_name << (t->parent->tags.size() == 1 ? "" : std::to_string(t->id)) << ","
			 << (t->is_thread ? "thread" :"space-time") << ","
			 << t->thread_id << ","
			 << t->addr_range.first << ","
			 << t->addr_range.second << ","
			 << t->x_range.first << ","
			 << t->x_range.second << ","
			 << t->access_count << "\n";
	}

	// Close files
	tag_file.flush();
       	tag_file.close();
	if (clear_tags) {
		for (auto& tag_iter : all_tags) {
			delete tag_iter.second;
		}
		all_tags.clear();
	} else {
		reset_tags_for_new_file();
	}
	
}


void open_trace_files() {
	std::stringstream s;
	s << output_trace_path << "_" << file_count;
	full_output_trace_path = s.str();
	file_count++;
	  
	output_tagfile_path = DefaultOutputPath + "/" + s.str() + TagFileSuffix;
	std::string output_trace_path = DefaultOutputPath + "/" + s.str() + TraceSuffix;

	mkdir(DefaultOutputPath.c_str(), 0755);
	
	std::cerr << "Opening trace '" << s.str() << "'.\n";
	unlink(output_trace_path.c_str());
	trace_writer = new TraceWriter(output_trace_path);

	for (auto thread: thread_ids) {
		std::stringstream name;
		name << "thread-" << thread.first;
		if (all_tags.find(name.str()) == all_tags.end()) {
			auto t =  new TagData(name.str(), (ADDRINT)-1,0, true, thread.first);
			all_tags[name.str()] = t;
			thread_ids[thread.first] = t;
		}
	}

	curr_traced_lines = 0;
}


void write_stats_file() {
	//curr_traced_lines << " memory requests in trace '" << full_output_trace_path << "'.\n";
	float hit_rate = (hits+0.0)/(hits+misses+1.0);
	float miss_per_inst = (misses+0.0)/(inst_count+1.0);
	
	std::string stats_file_name =  DefaultOutputPath + "/" + full_output_trace_path + StatsFileSuffix;
	
	std::ofstream stats_file(stats_file_name);
	
	stats_file << "app,file_no,m_cache_lines,m_cache_line_size,m_cache_size,m_inst_count,m_hit_rate,m_miss_per_inst\n";
	stats_file << output_trace_path << "," <<
		file_count << "," <<
		cache_size << "," << 
		cache_line << "," << 
		(cache_line*cache_size) << "," << 
		inst_count << "," <<
		hit_rate<< "," <<
		miss_per_inst << "\n";
	stats_file.close();
					 
}


void close_trace_files(bool clear_tags) {
	write_stats_file();

	std::string output_metadata_path = DefaultOutputPath + "/" + full_output_trace_path + MetaFileSuffix;
	std::ofstream meta_file (output_metadata_path);
	meta_file << cache_size << " " << cache_line <<"\n";
	for(auto & thread: thread_ids) {
		meta_file << thread.first << " ";
	}
	if (thread_ids.find(0) == thread_ids.end()) {
		meta_file << 0 << " ";
	}
	meta_file << "\n";
	meta_file.flush();
	meta_file.close();


	inst_count = 0;
	if (KnobFlushCacheOnNewFile.Value()) {
		flush_cache();
	}
	
	write_tags_and_clear(clear_tags);
	delete trace_writer;
}

VOID write_to_memfile(ADDRINT addr, int acc_type, THREADID threadid) {

	trace_writer->write_data_mem(addr, acc_type, threadid);
	curr_traced_lines++; // Afterward, for 0-based indexing
	total_traced_lines++;

	// print a progress status message every DefaultMaximumLines
	if (total_traced_lines >= DefaultMaximumLines && total_traced_lines % DefaultMaximumLines == 0)
	{
		std::cout << " ------ PROGRESS Compeleted Number of Accesses: " << total_traced_lines << "\n";
	}

	if(curr_traced_lines >= max_lines) { // If reached file size limit, exit
		if (file_count >= KnobFileCount.Value()) {
			std::cerr << "Exiting application early\n";
			exit_early(0);
		} else {
			std::cerr << "Creating new trace file\n";
			close_trace_files(false);// false preserves the tags
			open_trace_files();
		}
	}
}

VOID new_trace_called(VOID * trace_name) {
	BE_THREAD_SAFE();
	close_trace_files(true);
	file_count = 0;
	output_trace_path = (char*)trace_name;
	open_trace_files();
}

TagData * do_dump_start(VOID * tag_name, ADDRINT low, ADDRINT hi, bool create_new, bool is_thread, THREADID thread_id) {
	char* s = (char *)tag_name;
	std::string str_tag (s);
	TagData * r;
	std::cerr << "Tag Started: " << str_tag <<"\n";
	if (DEBUG) {
		std::cerr << "Dump define called - " << low << ", " << hi << " TAG: " << str_tag << "\n";
	}


	if (all_tags.find(str_tag) == all_tags.end()) { // New tag
		if (DEBUG) {
			std::cerr << "Dump begin called - New tag Tag: " << str_tag << "\n";
			std::cerr << "Range: " << low << ", " << hi << "\n";
		}

		r = new TagData(str_tag, low, hi, is_thread, thread_id);
		all_tags[str_tag] = r;
    
	} else { // Reuse tag
		if (DEBUG) {
			std::cerr << "Dump define called - Old tag\n";
		}

		// Exit program if redefining tag
		r = all_tags[str_tag];
#if(0)
		if (r->addr_range.first != low || // Must be same range
		    r->addr_range.second != hi) {
			std::cerr << "Error: Tag '" << str_tag << "' redefined - Tag can't map to different ranges\n"
				"Exiting Trace Early...\n";
			exit_early(0);
		}
#endif

		r->addr_range =  std::pair<ADDRINT, ADDRINT>(low, hi);
    
		if (create_new) {
			r->create_new_tag();
		} else {
			r->tags.back()->active = true;
		}
	}
	return r;
}

VOID dump_start_called(VOID * tag_name, ADDRINT low, ADDRINT hi, bool create_new) {
	BE_THREAD_SAFE();
	do_dump_start(tag_name, low, hi, create_new, false, 0);
}

VOID tag_grow(VOID * tag_name, ADDRINT low, ADDRINT hi) {
	BE_THREAD_SAFE();
	auto tag = all_tags.find((char*)tag_name);
	if (tag == all_tags.end()) {
		std::cerr << "Tried to grow non-existant tag: " << (char*)tag_name << "\n";
		exit_early(0);
	}

	tag->second->addr_range.second = std::max(hi, tag->second->addr_range.second);
	tag->second->addr_range.second = std::max(low, tag->second->addr_range.second);
	tag->second->addr_range.first = std::min(hi, tag->second->addr_range.first);
	tag->second->addr_range.first = std::min(low, tag->second->addr_range.first);
}

VOID do_dump_stop(VOID * tag_name) {
	
	char *s = (char *)tag_name;
	std::string str_tag (s);
	std::cerr << "Tag stopped: " << str_tag <<"\n";
	if (DEBUG) {
		std::cerr << "End TAG: " << str_tag << "\n";
	}

	std::unordered_map<std::string, TagData*>::const_iterator iter = all_tags.find(str_tag);
	if (iter == all_tags.end()) {
		std::cerr << "Error: Stopping a tag that was never started: " << str_tag << "\n"
			"Exiting Trace Early...\n";
		exit_early(0);
	}
	for (std::vector<Tag*>::reverse_iterator i = iter->second->tags.rbegin();
	     i != iter->second->tags.rend(); ++i) {
		(*i)->active = false;
	}
}


VOID dump_stop_called(VOID * tag_name) {
	BE_THREAD_SAFE();
	do_dump_stop(tag_name);
}

bool instrumentation_started = false;

VOID signal_start() {
	BE_THREAD_SAFE();
	std::cerr << "Tracing Started\n";
	reached_start = true;

	if (!instrumentation_started) {
		std::cerr << "Turning on instrumentation\n";
		INS_AddInstrumentFunction(Instruction, 0);
		TRACE_AddInstrumentFunction(Trace, 0);
		instrumentation_started = true;
	}
}

VOID signal_stop() {
	BE_THREAD_SAFE();
	std::cerr << "Tracing Stopped\n";
	reached_start = false;
}

void dump_cache(std::ostream & out) {
	out << "Cache Lines\n";
	for(auto & line: accesses) {
		out << "addr: 0x" << line.first << " -> " << &(*line.second) <<"\n";
	}
	out << "LRU Stack\n";
	for(auto & lru: inorder_acc) {
		out << &lru << " " << lru << "\n";
	}
}

int get_thread_id() {
	return PIN_ThreadId();
}
#if (0)
#define cache_assert(exp)			\
	do {					\
		if(!(exp)) {			\
			dump_cache(std::cerr);	\
			assert(exp);		\
		}				\
	} while(0)
#else
#define cache_assert(exp)
#endif

/*
 * Returns: a value based on hit, miss, or compulsory miss
 * 0 - hit
 * 1 - miss
 * 2 - compulsory miss
 *
 */
int add_to_simulated_cache(ADDRINT addr) {
	int r;
	addr -= addr%cache_line; // Cache line modulus
	if (CACHE_DEBUG) {
		cache_writes++;
	}

	// classify access
	cache_assert(inorder_acc.size() == accesses.size());
	auto cache_iter = accesses.find(addr);
	if (all_accesses.find(addr) == all_accesses.end()) {
		r = COMP_MISS;
		if (CACHE_DEBUG) {
			comp_misses++;
		}
		misses++;
		all_accesses.insert(addr);
	} else if (cache_iter == accesses.end()) {
		r = CAP_MISS;
		if (CACHE_DEBUG) {
			cap_misses++;
			std::cerr << cache_writes << "th write (cap miss): " << addr << "\n";
		}
		misses++;
	} else {
		r = HIT;
		hits++;
	}
	cache_assert(inorder_acc.size() == accesses.size());

	if (r == COMP_MISS || r == CAP_MISS) {
		// on a miss, add the address the LRU stack and the map
		inorder_acc.push_front(addr);
		accesses[addr] = inorder_acc.begin();
		cache_assert(inorder_acc.size() == accesses.size());
		// if full, evict
		if (accesses.size() > cache_size) { 
			cache_assert(accesses.find(inorder_acc.back()) != accesses.end());
			accesses.erase(inorder_acc.back());
			inorder_acc.pop_back();
		}
		cache_assert(inorder_acc.size() == accesses.size());
	} else {
		// on a hit, move the addr to the top of the LRU stack
		inorder_acc.splice(inorder_acc.begin(), inorder_acc, cache_iter->second);
		cache_assert(inorder_acc.size() == accesses.size());
		if (CACHE_DEBUG && cache_writes%SkipRate == 0) {
			std::cerr << cache_writes << "th write (Hit): " << addr << "\n";
		}
	}
	return r;

}

int translate_cache(int access_type, bool read) {
	if (access_type == HIT) {
		return read ? READ_HIT : WRITE_HIT;
	} else if(access_type == CAP_MISS) {
		return read ? READ_CAP_MISS : WRITE_CAP_MISS;
	}
	return read ? READ_COMP_MISS : WRITE_COMP_MISS;
}


bool skipping = true;

VOID RecordMemAccess(THREADID thread_id, ADDRINT addr, bool is_read) {
	BE_THREAD_SAFE();
	if (DEBUG) {
		read_insts++;
	}
	all_lines++;

	if (skipping && all_lines>= SkipMemOps) {
		std::cerr << "Done skipping " << SkipMemOps << " ops\n";
		skipping = false;
	} 
	if (!reached_start || skipping) return;
	int access_type = translate_cache(add_to_simulated_cache(addr), is_read);


	bool is_tag_match = false;
	bool updated = false;
	// We do three things as we iterater through the tags:
	// 1.  we need to called `update` on tags to keep track of their address ranges.
	// 2.  we need to record the access (but only if update returned true for some tag.
	// 3.  We also need to ensure that we only trace memops outside of a  tag if !TaggedOnly. 
	for (auto& tag_iter : all_tags) {
		TagData* td = tag_iter.second;
		if (td->is_thread) {
			if(td->thread_id == thread_id){ 
				updated =  td->update(addr, curr_traced_lines) || updated;
			}
		} else {
			if (((td->addr_range.first == LIMIT || td->addr_range.first <= addr) &&
			     (td->addr_range.second == LIMIT || addr <= td->addr_range.second))) {
				is_tag_match = true;
				updated = td->update(addr, curr_traced_lines) || updated;
			}
		}

	}  
	if ((TaggedOnly && is_tag_match) || !TaggedOnly) {
		if (updated) {
			write_to_memfile(addr, access_type, thread_id);
		}
	}
}


/* Called when tracked program finishes or Pin_ExitApplication is called
 *
 * Fills up tag map file, cache file, closes files, destroys objects
 */
VOID Fini(INT32 code, VOID *v) {

	if (DEBUG) {
		std::cerr << "Number of read insts: " << read_insts << "\n";
	}
	if (CACHE_DEBUG) {
		std::cerr << "Number of compulsory misses: " << comp_misses << "\n";
		std::cerr << "Number of capacity misses: " << cap_misses << "\n";
	}

	close_trace_files(true);
  
	std::cerr << "Collected " << total_traced_lines << " memory requests\n";
}

// Is called for every instruction and instruments reads and writes
VOID Instruction(INS ins, VOID *v)
{

	// Instruments memory accesses using a predicated call, i.e.
	// the instrumentation is called iff the instruction will actually be executed.
	//
	// On the IA-32 and Intel(R) 64 architectures conditional moves and REP 
	// prefixed instructions appear as predicated instructions in Pin.
	UINT32 memOperands = INS_MemoryOperandCount(ins);
	// Iterate over each memory operand of the instruction.
	for (UINT32 memOp = 0; memOp < memOperands; memOp++)
	{
		const bool isRead = INS_MemoryOperandIsRead(ins, memOp);
		const bool isWrite = INS_MemoryOperandIsWritten(ins, memOp);
		if (isRead) {
			INS_InsertPredicatedCall(
				ins, IPOINT_BEFORE, (AFUNPTR)RecordMemAccess,
				IARG_THREAD_ID,
				IARG_MEMORYOP_EA, memOp,
				IARG_BOOL, true,
				IARG_END);
		}
		// Note that in some architectures a single memory operand can be 
		// both read and written (for instance incl (%eax) on IA-32)
		// In that case we instrument it once for read and once for write.
		if (isWrite) {
			INS_InsertPredicatedCall(
				ins, IPOINT_BEFORE, (AFUNPTR)RecordMemAccess,
				IARG_THREAD_ID,
				IARG_MEMORYOP_EA, memOp,
				IARG_BOOL, false,
				IARG_END);
		}
	}
}

VOID FindStartFunc(RTN rtn, VOID *v) {
	if (!RTN_Valid(rtn)) return;
	RTN_Open(rtn);
	const std::string function_name = PIN_UndecorateSymbolName(RTN_Name(rtn), UNDECORATION_NAME_ONLY);
	if (function_name == start_function) {
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)signal_start, IARG_END);
	}
	RTN_Close(rtn);
}

// Find the macro routines in the current image and insert a call
VOID FindFunc(IMG img, VOID *v) {
	
	RTN rtn = RTN_FindByName(img, DUMP_START.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)dump_start_called,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 2,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 3,
			       IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, TAG_GROW.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)tag_grow,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 2,
			       IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, NEW_TRACE.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)new_trace_called,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
			       IARG_END);
		RTN_Close(rtn);
	}

	rtn = RTN_FindByName(img, DUMP_STOP.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)dump_stop_called,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
			       IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, FLUSH_CACHE.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)flush_cache_user,
			       IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, M_START_TRACE.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)signal_start,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
			       IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, M_STOP_TRACE.c_str());
	if(RTN_Valid(rtn)){
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)signal_stop,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
			       IARG_FUNCARG_ENTRYPOINT_VALUE, 1,
			       IARG_END);
		RTN_Close(rtn);
	}
	rtn = RTN_FindByName(img, GET_THREAD_ID.c_str());
	if(RTN_Valid(rtn)){
		std::cerr << "replace get_thread_id\n";
		RTN_Replace(rtn, (AFUNPTR)get_thread_id);
	}
}

INT32 Usage() {
	std::cerr << "Tracks memory accesses and instruction pointers between dump accesses\n";
	std::cerr << "\n" << KNOB_BASE::StringKnobSummary() << "\n";
	return -1;
}

bool check_alnum(const std::string& str) {
	for (char c : str) {
		if (!std::isalnum(c) && c != '_') {
			return false;
		}
	}
	return true;
};

VOID PIN_FAST_ANALYSIS_CALL count_insts(ADDRINT c) {
	BE_THREAD_SAFE();
	inst_count += c;
}

VOID Trace(TRACE trace, VOID *v)
{
	// Visit every basic block  in the trace
	for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl))
	{
		// Insert a call to docount for every bbl, passing the number of instructions.
		// IPOINT_ANYWHERE allows Pin to schedule the call anywhere in the bbl to obtain best performance.
		// Use a fast linkage for the call.
		BBL_InsertCall(bbl, IPOINT_ANYWHERE, AFUNPTR(count_insts), IARG_FAST_ANALYSIS_CALL, IARG_UINT32, BBL_NumIns(bbl), IARG_END);
	}
}


VOID ThreadStart(THREADID threadid, CONTEXT *ctxt, INT32 flags, VOID *v)
{
	std::stringstream name;
	name << "thread-" << threadid;
		
	BE_THREAD_SAFE();
	TagData *r = do_dump_start((VOID*)name.str().c_str(), (ADDRINT)-1, 0, false, true, threadid);
	thread_ids[threadid] = r;
}


VOID ThreadStop(THREADID threadid, const CONTEXT *ctxt, INT32 flags, VOID *v)
{
	std::stringstream name;
	name << "thread-" << threadid;
		
	BE_THREAD_SAFE();
	do_dump_stop((VOID *)name.str().c_str());
	thread_ids.erase(threadid);
}

int main(int argc, char *argv[]) {
	//Initialize pin & symbol manager
	PIN_InitSymbols();
	if (PIN_Init(argc, argv)) return Usage();

	if (!PIN_MutexInit(&the_big_lock)) {
		std::cerr << "the_big_lock init has failed\n";
		return 1;
	}
  
	if (DEBUG) {
		std::cerr << "Debugging mode\n";
	}

	// User input
	output_trace_path = KnobOutputFileLong.Value();
	if (output_trace_path == "") {
		output_trace_path = KnobOutputFile.Value();
		if (output_trace_path == "") {
			output_trace_path = "default";
		}
	}
	if (!check_alnum(output_trace_path)) {
		std::cerr << "Output name (" << output_trace_path << ") can only contain alphanumeric characters or _\n";
		return -1;
	}

	start_function = KnobStartFunctionLong.Value();
	if (start_function == "") {
		start_function = KnobStartFunction.Value();
		if (start_function == "") {
			start_function = DefaultStartFunction;
		}
	}
	if (start_function == "main") { // Replace main with function that calls main
		start_function = DefaultStartFunction;
	}

	max_lines = KnobMaxOutputLong.Value();
	if (max_lines == 0) {
		max_lines = KnobMaxOutput.Value();
		if (max_lines == 0) {
			max_lines = DefaultMaximumLines;
		}
	}

	cache_size = KnobCacheSizeLong.Value();
	if (cache_size == 0) {
		cache_size = KnobCacheSize.Value();
		if (cache_size == 0) {
			cache_size = NumberCacheEntries;
		}
	}

	cache_line = KnobCacheLineSizeLong.Value();
	if (cache_line == 0) {
		cache_line = KnobCacheLineSize.Value();
		if (cache_line == 0) {
			cache_line = DefaultCacheLineSize;
		}
	}


	SkipMemOps = KnobSkipMemOps.Value();

	TaggedOnly = KnobOnlyTaggedAccesses.Value();

	std::cerr << "TaggedOnly =  " << TaggedOnly << "\n";
  
	if (INPUT_DEBUG) {
		std::cerr << "Max lines of trace: "   << max_lines <<
			"\n# of cache entries: " << cache_size <<
			"\nCache line size in bytes: " << cache_line << 
			"\nOutput trace file at: " << output_trace_path << 
			"\nStart function: " << start_function << "\n";
	}


	open_trace_files();

	// Add instrumentation
	IMG_AddInstrumentFunction(FindFunc, 0);
	RTN_AddInstrumentFunction(FindStartFunc, 0);
	//  INS_AddInstrumentFunction(Instruction, 0);
	//  TRACE_AddInstrumentFunction(Trace, 0);
	PIN_AddThreadStartFunction(ThreadStart, 0);
	PIN_AddThreadFiniFunction(ThreadStop, 0);
	PIN_AddFiniFunction(Fini, 0);

	if (DEBUG) {
		std::cerr << "Starting now\n";
	}
	PIN_StartProgram();


	return 0;
}
