from garden_care_guide import display_care_info

name, id, water, sun = display_care_info("white fir", "adult", "clay")

if "," in sun:
    sun_1 = sun.split(", ")
    print(sun_1[0])

    try:
        print(sun_1[1])
    except IndexError:
        pass

