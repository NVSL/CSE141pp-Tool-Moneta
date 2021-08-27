cmd_Release/moneta.node := ln -f "Release/obj.target/moneta.node" "Release/moneta.node" 2>/dev/null || (rm -rf "Release/moneta.node" && cp -af "Release/obj.target/moneta.node" "Release/moneta.node")
