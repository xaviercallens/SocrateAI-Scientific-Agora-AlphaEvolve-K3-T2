import Lake
open Lake DSL

package «lean_oracle» {
}

@[default_target]
lean_exe «rpc_server» {
  root := `Main
}