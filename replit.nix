{pkgs}: {
  deps = [
    pkgs.xdotool
    pkgs.xorg.libXi
    pkgs.xorg.libXtst
    pkgs.xorg.libXrender
    pkgs.xorg.libXext
    pkgs.xorg.libX11
    pkgs.xorg.xrandr
    pkgs.xorg.xorgserver
    pkgs.chromedriver
    pkgs.chromium
    pkgs.tesseract
  ];
}
