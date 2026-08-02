{
  description = "Python + uv dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          python3
          uv
        ];

        shellHook = ''
          echo "🐍 Python: $(python --version)"
          echo "⚡ uv: $(uv --version)"

          # Create a local virtual environment automatically
          if [ ! -d .venv ]; then
            uv venv
          fi

          source .venv/bin/activate
        '';
      };
    };
}
