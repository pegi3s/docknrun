def separate_text_by_indentation(text):
    lines = text.split('\n')
    matrix = [[]]  # Inicia a matriz
    stack = [matrix[0]]
    current_level = 0

    for line in lines: #vai ver linha a linha
        if not line.strip(): #para evitar ler linhas em branco
            continue

        indent_level = line.count('\t')
        line_content = line.strip()

        # Organiza a estrutura
        while indent_level < current_level:
            stack.pop()
            current_level -= 1
        while indent_level > current_level:
            current_level += 1
            sub_list = []
            stack[-1].append(sub_list)
            stack.append(sub_list)

        # Adiciona lista
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
            # Verificar se o "-" está imediatamente após o nome da imagem
            if line[image_index + len(image)] == "-":
                continue
            image_parts = line.split(":")
            if len(image_parts) == 2:
                versions.append(image_parts[1].strip())
    return versions


