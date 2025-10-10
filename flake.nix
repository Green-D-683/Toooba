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
      pkgs = nixpkgs.legacyPackages.${system};

      python = pkgs.python3.withPackages (python-pkgs: [
        python-pkgs.pyyaml
      ]);
    in {
      devShells.default = pkgs.mkShell {
        nativeBuildInputs = with pkgs; [
          bluespec
          python
          gnumake
          stdenv.cc
          libelf
          verilator
        ];
      };
    });
}
