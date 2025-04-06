import re
import random

file = 'BoSnoliePOE2v1.hideout'

def remove_vaal_and_randomize(input_file, output_file):
    """
    Reads the .hideout file line-by-line. 
    - Skips doodads if name contains 'Vaal'.
    - Randomizes 'r' if doodad name == 'Fringe Moss' AND block has 'fv': 2.
    - Preserves duplicates and all other lines as-is.
    """

    with open(input_file, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    output_lines = []

    inside_block = False
    block_lines = []
    doodad_name = None

    for line in lines:
        # 1) Check if we're starting a new doodad block
        match = re.match(r'^(\s*)"([^"]+)"\s*:\s*\{\s*$', line)
        if match and not inside_block:
            # We have something like:    "Some Doodad": {
            inside_block = True
            block_lines = [line]
            doodad_name = match.group(2)  # The text inside the quotes
            continue

        # 2) If we're inside a doodad block, collect lines until the closing brace
        if inside_block:
            block_lines.append(line)

            # Check if this line closes the block: '  },' or '  }'
            if re.match(r'^\s*\},?\s*$', line):
                # Done with this doodad block
                inside_block = False

                # 2a) If doodad_name has 'Vaal' => skip entirely
                '''
                if "Vaal" in doodad_name:
                    doodad_name = None
                    block_lines = []
                    continue'''

                # 2b) If doodad_name == 'Fringe Moss' and block has "fv": 2, randomize 'r'
                block_text = "".join(block_lines)
                if doodad_name == "Fringe Moss":# and re.search(r'^\s*"fv"\s*:\s*2\s*,?\s*$', block_text, flags=re.MULTILINE):
                    new_block_lines = []
                    for bline in block_lines:
                        # Replace any "r": some_number with a random r in 0..65535
                        bline = re.sub(
                            r'("r"\s*:\s*)(\d+)',
                            lambda m: m.group(1) + str(random.randint(0, 65535)),
                            bline
                        )
                        new_block_lines.append(bline)
                    output_lines.extend(new_block_lines)
                else:
                    # Otherwise, keep the block as is
                    output_lines.extend(block_lines)

                # Reset
                doodad_name = None
                block_lines = []
            # else, keep reading lines inside the block
        else:
            # 3) Not inside a doodad block => just copy the line verbatim
            output_lines.append(line)

    # 4) Write final text
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(output_lines)


if __name__ == "__main__":
    remove_vaal_and_randomize(file, "modified.hideout")
