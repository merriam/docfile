# Python 3
import re
import os


good_pattern_string = "^([a-z]+)_([a-z0-9]+)_((?:(?:19[6-9]\d)|(?:20[01]\d))(?:\d{4})?)_.+\.pdf$"
good_regex = re.compile(good_pattern_string)


def get_command():
    if True:
        print("""
          DeepFind (regex) - Find files including subirs
          Find (regex) - Find files by regular expression
          List - list files in directory.
          Poor - List poorly named files
          Rename (regex) (replacement) - Rename files by regular expression
          Scatter - Scatter good matches into the categories folders
          Yank (all|bad|top) - Move pdfs up to top level
          Quit - Quit the program
           """)
    cmd = input("Your command, sir?")
    return cmd

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
                print("Error, sir.  Target already exists:", new_name)
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
        elif match(words, "poor", 0):
            print ("\n".join(find_nonmatching_files(good_regex)))
        elif match(words, "rename", 2):
            regex = re.compile(words[1])
            rename_files(regex, words[2])
        elif match(words, "scatter", 0):
            scatter()
        elif match(words, "yank", 1):
            if words[1] not in ["all", "bad", "top"]:
                print("Sir, please use a named parameter.")
            else:
                yank(words[1])
        else:
            print("Sir, I do not understand the command word:", words[0]);

def yank(action):
    for dirpath, dirnames, filenames in os.walk("."):
        if dirpath == ".":
            continue
        if action == "top" and dirpath.count(os.sep) > 1:
            continue
        for f in filenames:
            if action == "bad" and good_regex.search(f):
                continue
            if re.search("\.pdf$", f):
                print("yanking ", os.path.join(dirpath, f))
                os.rename(os.path.join(dirpath, f), f)

def rename_files(regex, replacement):
    files = find_matching_files(regex)
    for f in files:
        newName = regex.sub(replacement, f)
        print ("from:", f);
        print ("to:  ", newName, "\n")
    go = input("Sir!  Do you want to change these " + str(len(files)) + " files?")
    if go.strip() == "yes":
        for f in files:
            newName = regex.sub(replacement, f)
            print("renaming", f, "to", newName)
            os.rename(f, newName)
    else:
        print("Sir, please say 'yes' next time.")


def find_nonmatching_files(regex):
    files = os.listdir();
    files = [f for f in files if not regex.search(f)]
    return files

def find_matching_files(regex):
    files = os.listdir();
    files = [f for f in files if regex.search(f)]
    return files

process_commands()
print("Sir, this program is gratified to be of use.")
