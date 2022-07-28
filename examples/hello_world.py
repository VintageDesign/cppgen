from CppBuilder import CppBuilder

generator = CppBuilder()
generator.include("iostream")

with generator.block("int main()"):
    output_text = "Hello World"
    generator.write_code('std::cout << "' + output_text + '"<< std::endl')
    generator.write_code("return 0")


generator.save("hello_world.cpp")
