# -*- coding: utf-8 -*-

# Nested menu used in main window

class Term:
    def __init__(self, term_id, name, definition, is_a):
        self.term_id = term_id
        self.name = name
        self.definition = definition
        self.is_a = is_a
        self.children = []

    def add_child(self, child):
        self.children.append(child)


def parse_obo_file(obo_text_data):
    terms = {}
    current_term = None

    lines = obo_text_data.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith('id:'):
            term_id = line.split(': ')[1]
            current_term = Term(term_id, None, None, None)
            terms[term_id] = current_term
        elif line.startswith('name:'):
            current_term.name = line.split(': ')[1]
        elif line.startswith('def:'):
            current_term.definition = line.split(': ')[1]
        elif line.startswith('is_a:'):
            is_a = line.split(': ')[1]
            current_term.is_a = is_a

    for term in terms.values():
        if term.is_a is not None:
            parent_term = terms[term.is_a]
            parent_term.add_child(term)

    return terms


def build_term_hierarchy_string(terms, term_id, indent=0):
    result = ""
    if term_id in terms:
        term = terms[term_id]
        result += '\t' * indent + f"{term.term_id} - {term.name}\n"
        for child in term.children:
            result += build_term_hierarchy_string(terms, child.term_id, indent + 1)
    return result


def hierarchy_structure(obo_text_data):
    terms = parse_obo_file(obo_text_data)

    # Find the root terms (terms with no 'is_a')
    root_terms = [term_id for term_id, term in terms.items() if term.is_a is None]

    # Build hierarchy for each root term
    hierarchy_string = ""
    for root_term_id in root_terms:
        hierarchy_string += build_term_hierarchy_string(terms, root_term_id)

    return hierarchy_string


def convert_ontology_categories_for_nested_button(text):
    lines = text.split('\n')
    json_output = []
    stack = []

    for line in lines:
        if line.strip() != '':
            indentation_level = line.count('\t')
            category_key, category_value = line.strip().split(' - ')

            while len(stack) > indentation_level:
                stack.pop()

            current_category = {f"{category_key} - {category_value}": []}
            if stack:
                stack[-1][list(stack[-1].keys())[0]].append(current_category)
            else:
                json_output.append(current_category)
            stack.append(current_category)

    return json_output


# Function to add images to the appropriate category in the dictionary
def add_image_to_category(categories, dio_id, image):
    for category in categories:
        for key, value in category.items():
            if key.startswith(dio_id):
                if isinstance(value, list):
                    value.append(image)
                else:
                    category[key] = [image]
                return True
            if isinstance(value, list):
                for subcat in value:
                    if isinstance(subcat, dict):
                        if add_image_to_category([subcat], dio_id, image):
                            return True
    return False


def organize_images_for_nested_menu(diaf_text_data, categories):
    lines = diaf_text_data.splitlines()
    for line in lines:
        dio_id, image = line.strip().split()
        add_image_to_category(categories, dio_id, image)
    categories = remove_prefix(categories)
    return categories


def remove_prefix(d):
    if isinstance(d, dict):
        return {k.split(" - ")[-1]: remove_prefix(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [remove_prefix(item) for item in d]
    else:
        return d
