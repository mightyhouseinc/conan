def get_mime_type(filepath):
    if filepath.endswith(".tgz"):
        return "x-gzip"
    elif filepath.endswith(".txz"):
        return "x-xz"
    else:
        return "auto"
