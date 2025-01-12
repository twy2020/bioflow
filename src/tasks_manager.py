import curses

def task_manager(stdscr, tasks):
    # 初始化颜色对
    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # 黄色
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # 绿色
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)     # 红色

    curses.curs_set(0)  # 隐藏光标

    current_page = 0
    tasks_per_page = 1  # 每页显示一个总任务
    col_width = 8  # 每列宽度

    while True:
        stdscr.clear()

        # 获取终端大小
        height, width = stdscr.getmaxyx()

        # 判断是否显示详细模式
        detailed_mode = width >= col_width * 7 + 10  # 表格需要的最小宽度

        start_idx = current_page * tasks_per_page
        end_idx = min(start_idx + tasks_per_page, len(tasks))

        try:
            # 遍历当前页的任务
            for i, task in enumerate(tasks[start_idx:end_idx], start=1):
                srp_id = task[0]
                stdscr.addstr(1, 2, f"Task: {srp_id}", curses.color_pair(1))  # 黄色

                if detailed_mode:
                    # 表头
                    headers = ["Sub-Task", " sra2fq", "  QC", " Trim", "Mapping", "  bam", " FPKM"]
                    header_line = "".join(header.ljust(col_width) for header in headers)
                    stdscr.addstr(3, 4, header_line)

                    # 子任务及其状态
                    for j, subtask in enumerate(task[1:], start=4):
                        srr_id = subtask[0]
                        stdscr.addstr(j, 4, srr_id.ljust(col_width), curses.color_pair(1))  # 黄色子任务 ID
                        
                        for k, step in enumerate(subtask[1:], start=1):
                            status = "√" if step == "done" else "x"
                            color = curses.color_pair(2) if step == "done" else curses.color_pair(3)
                            stdscr.addstr(j, 4 + k * col_width, status.center(col_width), color)  # 绿色 √ 或 红色 x
                else:
                    # 精简模式：只显示任务 ID 和整体状态
                    for j, subtask in enumerate(task[1:], start=4):
                        srr_id = subtask[0]
                        overall_status = "all done" if all(step == "done" for step in subtask[1:]) else "unfinished"
                        color = curses.color_pair(2) if overall_status == "all done" else curses.color_pair(3)
                        stdscr.addstr(j, 4, srr_id.ljust(col_width), curses.color_pair(1))  # 黄色子任务 ID
                        stdscr.addstr(j, 4 + col_width, overall_status.ljust(col_width), color)

            # 分页状态
            stdscr.addstr(height - 1, 2, f"Page {current_page + 1}/{(len(tasks) + tasks_per_page - 1) // tasks_per_page} (q to quit, ←/→ to navigate)")
        except curses.error:
            # 如果终端太小，提示调整大小
            stdscr.clear()
            stdscr.addstr(0, 0, "Terminal too small! Resize to view tasks.", curses.color_pair(3))

        stdscr.refresh()

        # 键盘输入
        key = stdscr.getch()
        if key == ord('q'):  # 退出
            break
        elif key == curses.KEY_RIGHT and current_page < (len(tasks) + tasks_per_page - 1) // tasks_per_page - 1:  # 下一页
            current_page += 1
        elif key == curses.KEY_LEFT and current_page > 0:  # 上一页
            current_page -= 1

def main():
    # 示例任务数据
    tasks = [
        ["SRP001", 
         ["SRR001", "done", "done", "unfinished", "done", "unfinished", "done"],
         ["SRR002", "done", "done", "done", "done", "done", "unfinished"]],
        ["SRP002", 
         ["SRR003", "unfinished", "done", "done", "unfinished", "done", "done"]],
    ]

    curses.wrapper(task_manager, tasks)

if __name__ == "__main__":
    main()
