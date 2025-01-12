import os
from logger import log
from colorama import Fore, Style


def file_exists_prompt(msg):
    """Helper function to get user input with a message."""
    while True:
        choice = input(f"{msg} (yes/no/re(rescan)): ").strip().lower()
        if choice in {"yes", "no", "re"}:
            return choice
        log.level_log('ERROR', "Invalid choice. Please enter 'yes', 'no', or 're'.")


def select_from_list(file_list, file_type):
    """Helper function to let user select from a list of files."""
    log.level_log('DEBUG', f"Multiple {file_type} files found. Please select one:")
    for i, f in enumerate(file_list, start=1):
        log.level_log('INFO', f"{i}: {f}")
    while True:
        try:
            choice = int(input(f"Enter the number of your choice (1-{len(file_list)}): "))
            if 1 <= choice <= len(file_list):
                return file_list[choice - 1]
        except ValueError:
            pass
        log.level_log('ERROR', "Invalid choice. Please enter a valid number.")


def scan_and_select(workspace_path):
    print()
    print(f"{Fore.YELLOW}* Check and select files * {Style.RESET_ALL}")
    results = {}

    # Step 1: Look for HISAT2 index files
    print()
    log.level_log('DEBUG', "Scaning for HISAT2 index...\n")
    index_dir = os.path.join(workspace_path, "hista2_build", "index")
    index_groups = {}

    # Group files by base name
    for root, _, files in os.walk(index_dir):
        ht2_files = [f for f in files if f.endswith(".ht2")]
        grouped_files = {}

        for f in ht2_files:
            # Extract the base name (excluding .N.ht2)
            parts = f.split(".")
            if len(parts) >= 2 and parts[-1] == "ht2" and parts[-2].isdigit():
                base = ".".join(parts[:-2])
                index = int(parts[-2])
                if base not in grouped_files:
                    grouped_files[base] = set()
                grouped_files[base].add(index)

        # Check for completeness of each group
        for base, indices in grouped_files.items():
            if indices and set(range(1, max(indices) + 1)) == indices:
                index_groups[base] = os.path.join(root, base)
            else:
                log.level_log('WARNING', f"Incomplete HISAT2 index detected for {base}. Missing files: "
                                        f"{[i for i in range(1, max(indices) + 1) if i not in indices]}")

    # Prompt user to select an index group
    Step2_flag = True
    if index_groups:
        while True:  # 添加循环以支持重新选择
            if len(index_groups) == 1:
                selected_index = list(index_groups.keys())[0]
                log.level_log('INFO', f"Found HISAT2 index: {selected_index}.")
                print()
                use = input(f"Use {selected_index} as the mapping index? (yes/no/re(rescan)): ").strip().lower()
                if use == "yes":
                    results["ht2_path"] = index_groups[selected_index]
                    Step2_flag = False
                    break  # 选择完成，退出循环
                elif use == "no":
                    print()
                    log.level_log('WARNING', "Skipping HISAT2 index selection.")
                    print()
                    Step2_flag = True
                    break  # 用户选择跳过，退出循环
                elif use == "re":
                    print()
                    log.level_log('DEBUG', "Rescanning for HISAT2 index...")
                    print()
                    continue  # 重新扫描
                else:
                    log.level_log('ERROR', "Invalid choice. Please enter 'yes', 'no', or 're'.")
            else:
                print()
                selected_index = select_from_list(list(index_groups.keys()), "HISAT2 index")
                log.level_log('DEBUG', f"User selected HISAT2 index: {selected_index}")
                print()
                use = input(f"Use {selected_index} as the mapping index? (yes/no/re(rechoice)): ").strip().lower()
                if use == "yes":
                    results["ht2_path"] = index_groups[selected_index]
                    Step2_flag = False
                    break  # 选择完成，退出循环
                elif use == "no":
                    print()
                    log.level_log('WARNING', "Skipping HISAT2 index selection.")
                    print()
                    Step2_flag = True
                    break  # 用户选择跳过，退出循环
                elif use == "re":
                    print()
                    log.level_log('DEBUG', "Rescanning for HISAT2 index...")
                    continue  # 重新扫描
                else:
                    log.level_log('ERROR', "Invalid choice. Please enter 'yes', 'no', or 're'.")

    if Step2_flag:
        log.level_log('WARNING', "No HISAT2 index files selected. Proceed to select a sequence file to build the index.")
        log.level_log('WARNING', "Missing HISAT2 index may prevent mapping in later steps.")

        # Step 2: Look for sequence files for building HISAT2 index
        print()
        log.level_log('DEBUG', "Looking for sequence files for building HISAT2 index...")
        src_dir = os.path.join(workspace_path, "hista2_build", "src")
        fasta_files = []
        for root, _, files in os.walk(src_dir):
            for f in files:
                if f.endswith(".fa") or f.endswith(".fasta") or not f.endswith("."):  # Allow unconventional formats
                    fasta_files.append(os.path.join(root, f))

        while True:
            if fasta_files:
                if len(fasta_files) == 1:
                    selected_file = fasta_files[0]
                    print()
                    log.level_log('DEBUG', f"Using {selected_file} for building HISAT2 index.")
                else:
                    selected_file = select_from_list(fasta_files, "FASTA")
                    print()
                    log.level_log('DEBUG', f"Using {selected_file} for building HISAT2 index.")
                with open(selected_file, 'r') as f:
                    first_char = f.read(1)
                if first_char != ">":
                    log.level_log('WARNING', "Selected file may not be in standard FASTA format. HISAT2 build may fail.")
                    use = input(f"Continue with this file? (yes/no): ").strip().lower()
                    if use == "yes":
                        results["hista2_build_fa"] = selected_file
                        break
                else:
                    results["hista2_build_fa"] = selected_file
                    break
            else:
                print()
                log.level_log('WARNING', "No sequence files found in HISAT2 build source directory.")
                log.level_log('WARNING', "Missing sequence file may prevent HISAT2 index creation.\n")
                choice = file_exists_prompt("Do you want to ignore this file and proceed(yes), rescan(re), or stop the program?(no)")
                if choice == "yes":
                    log.level_log('WARNING', "You chose to ignore the missing gene annotation file. Proceeding with the pipeline.")
                    break
                if choice == "no":
                    log.level_log('ERROR', "Process terminated by the user. Gene annotation file is required.")
                    exit(1)
                elif choice == "re":
                    print()
                    log.level_log('DEBUG', "Looking for sequence files for building HISAT2 index...")
                    # Rescan
                    fasta_files = []
                    for root, _, files in os.walk(src_dir):
                        for f in files:
                            if f.endswith(".fa") or f.endswith(".fasta") or not f.endswith("."):
                                fasta_files.append(os.path.join(root, f))
                else:
                    log.level_log('ERROR', "Process terminated by the user.")
                    exit(1)

    # Step 3: Look for gene annotation files
    print()
    log.level_log('DEBUG', "Looking for gene annotation files in gff_files/...")
    gff_dir = os.path.join(workspace_path, "gff_files")
    gff_files = []
    for root, _, files in os.walk(gff_dir):
        for f in files:
            if f.endswith(".gff") or f.endswith(".gff3"):
                gff_files.append(os.path.join(root, f))

    while True:
        if gff_files:
            if len(gff_files) == 1:
                selected_file = gff_files[0]
                print()
                log.level_log('DEBUG', f"Using {selected_file} as the gene annotation file.")
            else:
                selected_file = select_from_list(gff_files, "gene annotation")
                print()
                log.level_log('DEBUG', f"Using {selected_file} as the gene annotation file.")
            results["gene_annotation"] = selected_file
            break
        else:
            print()
            log.level_log('WARNING', "No gene annotation files found.")
            log.level_log('WARNING', "Missing gene annotation file may affect transcript assembly and quantification.\n")
            choice = file_exists_prompt("Do you want to ignore this file and proceed(yes), rescan(re), or stop the program?(no)")
            if choice == "yes":
                log.level_log('WARNING', "You chose to ignore the missing gene annotation file. Proceeding with the pipeline.\n")
                break
            elif choice == "no":
                log.level_log('ERROR', "Process terminated by the user. Gene annotation file is required.")
                exit(1)
            elif choice == "re":
                print()
                log.level_log('DEBUG', "Rescanning for gene annotation files...")
                gff_files = []
                for root, _, files in os.walk(gff_dir):
                    for f in files:
                        if f.endswith(".gff") or f.endswith(".gff3"):
                            gff_files.append(os.path.join(root, f))

    return results


# Example usage
if __name__ == "__main__":
    workspace_path = "/path/to/your/workspace"
    selected_files = scan_and_select(workspace_path)
    print("Selected files:", selected_files)
