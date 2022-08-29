import javalang

if __name__ == "__main__":
    tree = javalang.parse.parse("package javalang.brewtab.com; class Test {}")
    print(tree)

