import os
with open ('PIPELINE_NAME', 'r') as PIPELINE_NAME:
    PIPELINE_NAME=PIPELINE_NAME.read().strip()
    
with open('main.py', 'r') as main_file:
    main_file_ = main_file.read()
    function_name=PIPELINE_NAME
    main_file_ = main_file_.replace("def <<pipeline_name>>(request):", f"def {function_name}(request):")

with open(f"main.py", "w") as main_file_restructured:
    main_file_restructured.write(main_file_)