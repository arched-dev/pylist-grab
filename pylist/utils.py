import sys
import os


def run_silently(func, silence=True, *args, **kwargs):
    if silence:
        with open(os.devnull, 'w') as fnull:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = sys.stderr = fnull

            try:
                return_value = func(*args, **kwargs)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            return return_value
    else:
        return func(*args, **kwargs)
