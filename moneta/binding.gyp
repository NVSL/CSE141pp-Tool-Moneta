{
  "targets": [
    {
      "target_name": "libmoneta",
      "cflags!": [ "-fno-exceptions" ],
      "cflags_cc!": [ "-fno-exceptions" ],
      "sources": [
        #"./src/libmoneta.cpp",
        "./src/index.cpp"
      ],
      #"library_dirs": [ "\home\jovyan\work\moneta\src"],
      #"libraries": ["-libmoneta"],
      "include_dirs": [
        "<!@(node -p \"require('node-addon-api').include\")"
      ],
      'defines': [ 'NAPI_DISABLE_CPP_EXCEPTIONS' ],
    }
  ]
}
