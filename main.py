import cmd
import drawutils as d

class IO (cmd.Cmd):
    def do_demo(self, s):
        d.demo()
        return
    def do_exit(self, s):
        return True

if __name__ == "__main__":
    io = IO()
    io.cmdloop()
