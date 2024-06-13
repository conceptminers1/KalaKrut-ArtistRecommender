{pkgs}: {
  deps = [
    pkgs.python311Packages.gunicorn
    pkgs.glibcLocales
  ];
}
