import gopygo


if __name__ == "__main__":
    program = """
    package main
    
    import "fmt"
    
    func main() {
        fmt.Println("Hello, World!")
    }
    """
    program = program.lstrip()
    tree = gopygo.parse(program)
    
    text = gopygo.unparse(tree)
    print(text)
