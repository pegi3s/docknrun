#Finds Docker image versions. Used in the secondary window menu

def separate_text_by_indentation(text):
    lines = text.split('\n')
    matrix = [[]]  # Matrix initialization
    stack = [matrix[0]]
    current_level = 0

    for line in lines:
        if not line.strip(): # avoids reading blank lines 
            continue

        indent_level = line.count('\t')
        line_content = line.strip()

        # Organize the structure
        while indent_level < current_level:
            stack.pop()
            current_level -= 1
        while indent_level > current_level:
            current_level += 1
            sub_list = []
            stack[-1].append(sub_list)
            stack.append(sub_list)

        # Add list
        stack[-1].append(line_content)

    return matrix

def findImageVersions (image, imageList):
    versions = []
    print(image+"-gui")
    for line in imageList.split('\n'):
        if line.strip() == "":
            continue
        if image in line:
            image_index = line.index(image)
            # check if "-" is immediately after the image name
            if line[image_index + len(image)] == "-":
                continue
            image_parts = line.split(":")
            if len(image_parts) == 2:
                versions.append(image_parts[1].strip())
    return versions


