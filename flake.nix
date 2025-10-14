{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    systems.url = "github:nix-systems/default";

    flake-utils = {
      url = "github:numtide/flake-utils";
      inputs.systems.follows = "systems";
    };
  };

  outputs = {
    nixpkgs,
    flake-utils,
    ...
  }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree=true;
      };

      python = pkgs.python3.withPackages (python-pkgs: [
        python-pkgs.pyyaml
      ]);
    in {
      devShells.default = pkgs.mkShell rec {
        nativeBuildInputs = with pkgs; [
          bluespec
          python
          gnumake
          stdenv.cc
          libelf
          verilator
          quartus-prime-lite
        ];
        BLUESPEC_VERILOG_LIB="${pkgs.bluespec}/lib/Verilog";
        shellHook = ''
          rm -f BlueSpec-Verilog
          ln -s ${BLUESPEC_VERILOG_LIB} BlueSpec-Verilog
        '';
      };
    });
}
