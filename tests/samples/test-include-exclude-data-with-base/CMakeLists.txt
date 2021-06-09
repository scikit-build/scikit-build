cmake_minimum_required(VERSION 3.5.0)

project(test_include_exclude_data_with_base NONE)

set(base "src/")

set(module "${CMAKE_CURRENT_BINARY_DIR}/cmake_generated_module.py")
file(WRITE ${module} "# Generated from ${CMAKE_CURRENT_LIST_FILE}

def what():
    return \"cmake_generated_module\"

")
install(FILES ${module} DESTINATION ${base}hello)

# hello data
set(data "${CMAKE_CURRENT_BINARY_DIR}/hello_data1_cmake_generated.txt")
file(WRITE ${data} "# Generated from ${CMAKE_CURRENT_LIST_FILE}")
install(FILES ${data} DESTINATION ${base}hello)

set(data "${CMAKE_CURRENT_BINARY_DIR}/hello_data2_cmake_generated.txt")
file(WRITE ${data} "# Generated from ${CMAKE_CURRENT_LIST_FILE}")
install(FILES ${data} DESTINATION ${base}hello)

set(data "${CMAKE_CURRENT_BINARY_DIR}/hello_data3_cmake_generated.txt")
file(WRITE ${data} "# Generated from ${CMAKE_CURRENT_LIST_FILE}")
install(FILES ${data} DESTINATION ${base}hello/data/subdata)

set(data "${CMAKE_CURRENT_BINARY_DIR}/hello_data4_cmake_generated_and_exclude_from_setup.txt")
file(WRITE ${data} "# Generated from ${CMAKE_CURRENT_LIST_FILE}")
install(FILES ${data} DESTINATION ${base}hello/data/subdata)

# hello2 data
set(data "${CMAKE_CURRENT_BINARY_DIR}/hello2_data1_cmake_generated.txt")
file(WRITE ${data} "# Generated from ${CMAKE_CURRENT_LIST_FILE}")
install(FILES ${data} DESTINATION ${base}hello2)

set(data "${CMAKE_CURRENT_BINARY_DIR}/hello2_data2_cmake_generated.txt")
file(WRITE ${data} "# Generated from ${CMAKE_CURRENT_LIST_FILE}")
install(FILES ${data} DESTINATION ${base}hello2)

set(data "${CMAKE_CURRENT_BINARY_DIR}/hello2_data3_cmake_generated.txt")
file(WRITE ${data} "# Generated from ${CMAKE_CURRENT_LIST_FILE}")
install(FILES ${data} DESTINATION ${base}hello2/data2/subdata2)

set(data "${CMAKE_CURRENT_BINARY_DIR}/hello2_data4_cmake_generated_and_exclude_from_setup.txt")
file(WRITE ${data} "# Generated from ${CMAKE_CURRENT_LIST_FILE}")
install(FILES ${data} DESTINATION ${base}hello2/data2/subdata2)
