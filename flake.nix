{
  description = "A tool for creating projects similar to IDEs";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        python = pkgs.python3;
        pythonPackages = pkgs.python3Packages;

        inherit (pythonPackages) buildPythonApplication;
      in {

        packages = rec {
          create-project = buildPythonApplication {
            pname = "create-project";
            version = "0.1.1";
            src = ./.;

            propagatedBuildInputs = with pythonPackages; [ pyyaml inquirer ];
          };
          default = create-project;
        };

        devShell = with pkgs;
          mkShell {
            buildInputs = [
              (python.withPackages (p: with p; [ setuptools pyyaml inquirer ]))
              pyright
              pythonPackages.flake8
              pythonPackages.autopep8
            ];
          };

      });
}
