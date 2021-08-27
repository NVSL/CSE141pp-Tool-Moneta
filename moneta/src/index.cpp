#include <napi.h>
#include <iostream>
#include <string>
#include <cstring>
#include "../pin_tags.h"

using namespace Napi;

    void JS_DUMP_START_ALL(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (info.Length() < 2) {
            Napi::TypeError::New(env, "Invalid arguments").ThrowAsJavaScriptException();
        } 

        // Napi::String tag = info[1].As<Napi::String>();

        // Convert our first arg into a C++ const char*
        std::string tag_str = info[0].ToString().Utf8Value(); // Takes a Napi Value, converts it to a Napi string, then converts to a UTF C string
        const char* tag = tag_str.c_str(); // Takes the memory location of the string as a pointer

        // Convert our second arg into a boolean
        Napi::Boolean create_new = info[1].As<Napi::Boolean>();

        // Call our C++ function with our converted args
        DUMP_START_ALL(tag, create_new);
    }

    void JS_DUMP_STOP(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (info.Length() < 1) {
            Napi::TypeError::New(env, "Invalid arguments").ThrowAsJavaScriptException();
        } 

        // Convert our first arg into a C++ const char*
        std::string tag_str = info[0].ToString().Utf8Value(); // Takes a Napi Value, converts it to a Napi string, then converts to a UTF C string
        const char* tag = tag_str.c_str(); // Takes the memory location of the string as a pointer

        DUMP_STOP(tag);
    }
    
    void JS_NEW_TRACE(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (info.Length() < 1) {
            Napi::TypeError::New(env, "Invalid arguments").ThrowAsJavaScriptException();
        } 

        // Convert our first arg into a C++ const char*
        std::string s_str = info[0].ToString().Utf8Value(); // Takes a Napi Value, converts it to a Napi string, then converts to a UTF C string
        const char* s = s_str.c_str(); // Takes the memory location of the string as a pointer

        NEW_TRACE(s);
    }

    void JS_FLUSH_CACHE(const Napi::CallbackInfo& info) {
        // Napi::Env env = info.Env();
        FLUSH_CACHE();
    }

    void JS_STOP_TRACE(const Napi::CallbackInfo& info) {
        // Napi::Env env = info.Env();
        STOP_TRACE();
    }

    
    void JS_START_TRACE(const Napi::CallbackInfo& info) {
        // Napi::Env env = info.Env();
        START_TRACE();
    }


	Napi::Object Init(Napi::Env env, Napi::Object exports) {
        exports.Set(Napi::String::New(env, "JS_START_TRACE"), Napi::Function::New(env, JS_START_TRACE));
        exports.Set(Napi::String::New(env, "JS_DUMP_START_ALL"), Napi::Function::New(env, JS_DUMP_START_ALL));
        exports.Set(Napi::String::New(env, "JS_STOP_TRACE"),Napi::Function::New(env, JS_STOP_TRACE));
        exports.Set(Napi::String::New(env, "JS_NEW_TRACE"), Napi::Function::New(env, JS_NEW_TRACE));
        exports.Set(Napi::String::New(env, "JS_FLUSH_CACHE"), Napi::Function::New(env, JS_FLUSH_CACHE));
        exports.Set(Napi::String::New(env, "JS_DUMP_STOP"), Napi::Function::New(env, JS_DUMP_STOP));
        exports.Set(Napi::String::New(env, "JS_DUMP_START_ALL"), Napi::Function::New(env, JS_DUMP_START_ALL));

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