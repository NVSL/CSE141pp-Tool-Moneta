#include <napi.h>
#include <string>
#include "../pin_tags.h"

using namespace Napi;

    Napi::String JS_DUMP_START_ALL(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (info.Length() < 3) {
            Napi::TypeError::New(env, "Invalid arguments").ThrowAsJavaScriptException();
        } 

        Napi::String tag = info[1].As<Napi::String>();
        Napi::Boolean create_new = info[2].As<Napi::Boolean>();

        DUMP_START_ALL(tag, create_new);

        std::string result = "Dump Start All...";

        return Napi::String::New(env, result);
    }

    Napi::String JS_DUMP_STOP(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (info.Length() < 2) {
            Napi::TypeError::New(env, "Invalid arguments").ThrowAsJavaScriptException();
        } 

        Napi::String tag = info[1].As<Napi::String>();

        DUMP_STOP(tag);

        std::string result = "Dump Stop...";

        return Napi::String::New(env, result);
    }

    Napi::String JS_FLUSH_CACHE(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        FLUSH_CACHE();

        std::string result = "Flushing Cache...";

        return Napi::String::New(env, result);
    }

    Napi::String JS_STOP_TRACE(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        STOP_TRACE();

        std::string result = "Stopping Trace...";

        return Napi::String::New(env, result);
    }

    
    Napi::Function JS_START_TRACE(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        START_TRACE();

        std::string result = "Starting Trace...";

        // return Napi::String::New(env, result);
    }

	Napi::Object Init(Napi::Env env, Napi::Object exports) {
        exports.Set(
            Napi::String::New(env, "JS_START_TRACE"),
            Napi::Function::New(env, JS_START_TRACE),
            Napi::String::New(env, "JS_STOP_TRACE"),
            Napi::Function::New(env, JS_STOP_TRACE),
            Napi::String::New(env, "JS_FLUSH_CACHE"),
            Napi::Function::New(env, JS_FLUSH_CACHE),
            Napi::String::New(env, "JS_DUMP_STOP"),
            Napi::Function::New(env, JS_DUMP_STOP),
            Napi::String::New(env, "JS_DUMP_START_ALL"),
            Napi::Function::New(env, JS_DUMP_START_ALL)
        );

        return exports;
    }


/*
    void START_TRACE {
		M_START_TRACE(true, true);
	}
	void STOP_TRACE() {
		M_STOP_TRACE(true, true);
	}
	
	void NEW_TRACE(const char *s) {
		M_NEW_TRACE(s);
	}
*/

    NODE_API_MODULE(libmoneta, Init)