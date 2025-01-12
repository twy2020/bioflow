from art import text2art

# 使用更复杂的字体
banner_block = text2art("BIOFLOW", font="block")
banner_starwars = text2art("BIOFLOW", font="starwars")
banner_big = text2art("BIOFLOW", font="big")

# 打印不同字体的艺术字
print("Block font:\n", banner_block)
print("Starwars font:\n", banner_starwars)
print("Big font:\n", banner_big)
