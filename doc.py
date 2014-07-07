#!/usr/bin/env python2
import re
import os
import filecmp
import shutil

#good_pattern_string = r"^([a-z]+)_([a-z0-9]+)_((?:(?:19[6-9]\d)|(?:20[01]\d))(?:\d{4})?)_.+\.pdf$"
good_pattern_string = r"^([a-zA-Z0-9]+)_([a-zA-Z0-9]+)_(\d{8}|\d{4})(?:_.*)?\.pdf$"
g = good_pattern_string
near_pattern_string = r"^[^_]+_[^_]+_([0-9]{5,7}|[0-9]{9,12})(_.*)?\.pdf"
n = near_pattern_string
near_regex = re.compile(near_pattern_string)
    # close enough that it might have meant to be.
good_regex = re.compile(good_pattern_string)

def test_regex():
    good = ["tax_2011_20120304_more_stuff.pdf",
            "a_b_20120304.pdf", "a_b_2012.pdf"]
    near = ["fin_thing_2014021_more.pdf", "fin_2_201402221.pdf"]
    bad = ["foo.bar", "a.pdf", "a_b.pdf"]
    for name in good:
        assert good_regex.search(name), "{} should be good".format(name)
    for name in near:
        assert not good_regex.search(name), "{} should not be good.".format(name)
        assert near_regex.search(name), "{} should be near.".format(name)
    for name in bad:
        assert not good_regex.search(name), "{} should not be good.".format(name)
        assert not near_regex.search(name), "{} should not be near.".format(name)

def get_command():
    if True:
        print("""
          DeepFind (regex) - Find files including subirs
          Find (regex) - Find files by regular expression
          Grab - Grab all pdfs into ScanSnap dir.
          List - list files in directory.
          Poor - List poorly named files
          Rename (regex) (replacement) - Rename files by regular expression
          Scatter - Scatter good matches into the categories folders
          Update (path) - Update, copying new files for given directory.
          Yank (all|bad|top) - Move pdfs up to top level
          Quit - Quit the program
           """)
    cmd = raw_input("Your command, sir?")
    return cmd

def files_are_equal(name1, name2):
    try:
        return filecmp.cmp(name1, name2, shallow=False)
    except OSError:  # usually, one not existing.
        return False

def scatter():
    one_level_ok = False
    files = find_matching_files(good_regex)
    for f in files:
        first, second = good_regex.search(f).groups()[:2]
        # safe, because we know it matches the good file regex
        dir_name = os.path.join(first, second)
        new_name = os.path.join(first, second, f)
        if os.path.isdir(dir_name):
            if os.path.exists(new_name):
                # Target exists.  Is it identical?
                if files_are_equal(f, new_name):
                    print "{} is a pure duplicate, removing...".format(f)
                    os.unlink(f)
                else:
                    print "{} ERROR:  Different target named {} already exists".format(f, new_name)
            else:
                print("Move from:", f)
                print("       to:", new_name)
                os.rename(f, new_name)
        elif one_level_ok:
            # try just one level down
            dir_name = os.path.join(first)
            new_name = os.path.join(first, f)
            if os.path.isdir(dir_name):
                if os.path.exists(new_name):
                    print("Error, sir.  Target already exists:", new_name)
                else:
                    print("Move from:", f)
                    print("       to:", new_name)
                    os.rename(f, new_name)
            else:
                print("Error, sir.   No directory named", dir_name)

def fix_name(a):
    """ Return fixed name of a file or directory.

    The idea is return a name that would match after symbolic links, user names, irrelevant case, etc.
    """
    return os.path.abspath(os.path.realpath(os.path.expanduser(a))).lower()


def same_name(a, b):
    """ Return true if a and b are the same file or directory name.  """
    return fix_name(a) == fix_name(b)

def grab_all_pdfs():
    """ grab all pdfs from anywhere under top_level_pdf_files into the scansnap_top directory.

    Don't grab things correctly placed in the scansnap directory. """
    top_level_pdf_dirs = [fix_name("~")]
    ignore_dirs = ["~/.trash", "~/Library/Mail",
                   "~/Library/Application Support/TurboTax 2013/Forms",
                   "~/Library/Application Support/com.intuit.Turbotax.2012/Forms"]
    ignore_dirs = [ fix_name(p) for p in ignore_dirs ]
    scansnap_top = fix_name('~/documents/scansnap/')

    test_regex()

    for top in top_level_pdf_dirs:
        for dirname, _, filenames in os.walk(top):
            abs_dirname = fix_name(dirname)
            if any([abs_dirname.startswith(p) for p in ignore_dirs]):
                continue
            for fragment in filenames:
                match = good_regex.match(fragment)
                if match:
                    if same_name(abs_dirname, scansnap_top):
                        continue  # That's where they would go
                    if abs_dirname.startswith(scansnap_top):
                        sub_dirs = abs_dirname[len(scansnap_top)+1:].split(os.sep)
                        match_dirs = list(match.groups()[:2])  # file name's words
                        if sub_dirs == match_dirs:
                            continue   # in correct place, no reporting
                    filename = os.path.join(dirname, fragment)
                    destination = os.path.join(scansnap_top, fragment)
                    if os.path.exists(destination):
                        print("{}: ERR, File with that name exists in snapscan.".format(filename))
                        continue
                    print("{}: Moved". format(filename))
                    os.rename(filename, destination)
                elif near_regex.match(fragment):
                    filename = os.path.join(dirname, fragment)
                    print("{}:  Near Miss, probably badly named file".format(filename))

def process_commands():
    def match(words, command_name, args):
        if len(words) > 0 and command_name.lower().startswith(words[0].lower()):
            if len(words) - 1 != args:
                print("Sir, you have the wrong number of arguments for the",
                        command_name, "command")
                return False
            return True
        return False

    while True:
        words = get_command().split()
        if len(words) == 0:
            continue
        if match(words, "quit", 0):
            return
        elif match(words, "list", 0):
            print("=============\nPoorly named files:\n============")
            print("\n".join(find_nonmatching_files(good_regex)))
            print("\n=============\nWell named files:\n============")
            print("\n".join(find_matching_files(good_regex)))
        elif match(words, "deepfind", 1):
            regex = re.compile(words[1])
            for dirname, dirnames, filenames in os.walk("."):
                printed_header = False
                if "\\.organizer" in dirname:
                    continue   # cruft results
                for f in filenames:
                    if regex.search(f):
                        if not printed_header:
                            print("=== IN DIRECTORY", dirname, "===")
                            printed_header = True
                        print(f)
        elif match(words, "find", 1):
            regex = re.compile(words[1])
            print ("\n".join(find_matching_files(regex)))
        elif match(words, "grab", 0):
            grab_all_pdfs()
        elif match(words, "poor", 0):
            print ("\n".join(find_nonmatching_files(good_regex)))
        elif match(words, "rename", 2):
            regex = re.compile(words[1])
            rename_files(regex, words[2])
        elif match(words, "scatter", 0):
            scatter()
        elif match(words, "update", 0):
            update()
        elif match(words, "yank", 1):
            if words[1] not in ["all", "bad", "top"]:
                print("Sir, please use a named parameter.")
            else:
                yank(words[1])
        else:
            print("Sir, I do not understand the command word:", words[0])

def yank(action):
    for dirpath, dirnames, filenames in os.walk("."):
        if dirpath == ".":
            continue
        if action == "top" and dirpath.count(os.sep) > 1:
            continue
        for f in filenames:
            if action == "bad" and good_regex.search(f):
                continue
            if re.search(r"\.pdf$", f):
                print("yanking ", os.path.join(dirpath, f))
                os.rename(os.path.join(dirpath, f), f)

def rename_files(regex, replacement):
    files = find_matching_files(regex)
    for f in files:
        newName = regex.sub(replacement, f)
        print ("from:", f)
        print ("to:  ", newName, "\n")
    go = raw_input("Sir!  Do you want to change these " + str(len(files)) + " files?")
    if go.strip() == "yes":
        for f in files:
            newName = regex.sub(replacement, f)
            print("renaming", f, "to", newName)
            os.rename(f, newName)
    else:
        print("Sir, please say 'yes' next time.")

def find_nonmatching_files(regex):
    files = os.listdir('.')
    files = [f for f in files if not regex.search(f)]
    return files

def find_matching_files(regex):
    files = os.listdir('.')
    files = [f for f in files if regex.search(f)]
    return files

def update():
    cruft = [".ds_store"]
    print "Sorry, sir.  I'll need to ask for paths separately because of spaces."
    from_path = raw_input("FROM, where we copy new pdfs from?")
    to_path = raw_input("TO, where to copy over existing pdfs?")
    if not from_path:
        from_path = "/Volumes/Data/Manual Backups/20140707ScanSnap/"
        from_path = "~/documents/scan2/"
    if not to_path:
        to_path = "~/documents/scansnap/"
    from_path = fix_name(from_path)
    to_path = fix_name(to_path)
    print "updating from {} to {}".format(from_path, to_path)
    for raw_dir_name, _, filenames in os.walk(from_path):
        from_dir = fix_name(raw_dir_name)
        for name in filenames:
            if from_dir == from_path or good_regex.search(name):
                if any([name == bad for bad in cruft]):
                    continue
                # OK, this should probably move.
                from_file = os.path.join(from_dir, name)
                from_subdir = from_dir[len(from_path)+1:]
                to_dir = os.path.join(to_path, from_subdir)
                to_file= os.path.join(to_dir, name)
                print "{} =? {}".format(from_file, to_file)
                if files_are_equal(from_file, to_file):
                    continue
                elif os.path.exists(to_file):
                    print "{} ERROR.  Does not match exiting file {}".format(from_file, to_file)
                    continue
                else:
                    copy_file(from_file, to_file)
                    print "{}:  copied".format(name)

def copy_file(from_file, to_file):
    # So, standard library is just broken.   I can copy, but will
    # loose all my metadata.
    shutil.copy2(from_file, to_file)

process_commands()
print("Sir, this program is gratified to be of use.")
