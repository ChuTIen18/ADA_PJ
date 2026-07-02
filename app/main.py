from algorithms.cms import CountMinSketch
from algorithms.cms_mixed import MixedCMS


print("========== COUNT-MIN SKETCH ==========\n")

width = int(input("Width: "))

depth = int(input("Depth (Classic CMS): "))

cms = CountMinSketch(width, depth)

n = int(input("\nNumber of stream items: "))

print()

for i in range(n):

    item = input(f"Item {i+1}: ")

    cms.update(item)

print("\nSketch created successfully!")

cms.display()

print("\n========== QUERY ==========")

while True:

    item = input("\nQuery item: ")

    print("Estimated frequency =", cms.query(item))

    choice = input("\nContinue? (y/n): ")

    if choice.lower() != "y":
        break


print("\n========== MIXED CMS DEMO ==========\n")

mixed = MixedCMS(width)

n = int(input("Number of stream items: "))

for i in range(n):

    item = input(f"Item {i+1}: ")

    k = int(input("Hash functions used (2~5): "))

    mixed.update(item, k)

print("\nMixed CMS Sketch")

mixed.display()

print("\n========== QUERY ==========")

while True:

    item = input("\nQuery item: ")

    k = int(input("Hash functions (2~5): "))

    print("Estimated frequency =", mixed.query(item, k))

    if input("\nContinue? (y/n): ").lower() != "y":
        break
