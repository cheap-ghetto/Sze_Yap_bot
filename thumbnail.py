import discord
import random

chinese_food_png = ['3eggtarts_rough.png', '3eggtarts_smooth.png', 'cantonese_flaky_pastry.png',
                    'cheung_fun_with_soya_sauce.png', 'chinese_fried_rice_bowl_on_placement_mat.png',
                    'chinese_fried_rice_brown.png', 'chinese_fried_rice_with_egg.png', 'coconut_mochi.png',
                    'dimsum_6_plates_birdview.png', 'dimsum_bowls_side_birdview.png',
                    'dimsum_dog_pig__sweet_buns.png', 'dimsum_multiple_bowls.png', 'dimsum_restaurant_table.png',
                    'dimsum_shrimp_dumplings.png', 'dimsum_sumai.png', 'dimsum_white_bun_with_soya_sauce.png',
                    'mooncakes_on_plate.png', 'orange_chicken.png', 'purple_glutinous_rice_dessert.png',
                    'raspberry_shredded_coconut_jelly.png', 'soy_sauce_noodles.png', 'soy_sauce_noodles_bowl.png',
                    'specialty_jelly_cube_with_umbrella.png', 'tong_yuen_rainbow_ball_dessert.png',
                    'tong_yuen_rainbow_ball_dessert_dark.png', 'water_chestnut_cake.png']

cute_cats_gifs = ['cute_cat_dance_360_sparkles.gif', 'cute_cat_dance_happy.gif',
                  'cute_cat_ears_wiggling_with_fish.gif', 'cute_cat_eating_noodles.gif', 'cute_cat_eating_pizza.gif',
                  'cute_cat_face_squish.gif', 'cute_cat_hands_move.gif', 'cute_cat_hehe_sneaky.gif',
                  'cute_cat_hello_box_grey_cat.gif', 'cute_cat_hello_box_white_cat.gif',
                  'cute_cat_jumping_excited.gif', 'cute_cat_laughing_with_fish.gif', 'cute_cat_ok_wink_heart.gif',
                  'cute_cat_rawr.gif', 'cute_cat_thinking.gif', 'cute_cat_two_chilling.gif', 'cute_cat_waiting.gif',
                  'cute_cat_waiting_black_background.gif', 'cute_cat_waiting_on_phone.gif', 'cute_cat_wowee.gif',
                  'cute_cat_yay_jump.gif']

cute_fish_gifs = ['baby_dory_laughing.gif', 'cute_fish_blue.gif']

general_tourist_png = ['i_heart_toisan.png', 'taishan_chinese_character.png', 'Taishan_county_map.png',
                       'taishan_white_word_against_background.png']

cat_word = ['cat', 'feline', 'meow', 'kitten']

food_word = ['food', 'noodles', 'egg tart', 'dim sum', 'fried rice']

fish_word = ['fish', '鱼', '魚']

general_tourist_word = ['taishan', 'hoisan']


class Pictures:

    def __init__(self):
        self.gif = random.choice(cute_fish_gifs + cute_cats_gifs)
        self.food = random.choice(chinese_food_png)
        self.cat = random.choice(cute_cats_gifs)
        self.fish = random.choice(cute_fish_gifs)


def check_thumbnail(poss_word, word_phrase):

    file = None

    for word in poss_word[8].lower().split():
        if word in cat_word:
            chosen_picture = random.choice(cute_cats_gifs)
            file = discord.File("pictures/" + chosen_picture, filename="image.gif")
        elif word in food_word:
            chosen_picture = random.choice(chinese_food_png)
            file = discord.File("pictures/" + chosen_picture, filename="image.gif")
        elif word in cute_fish_gifs:
            chosen_picture = random.choice(cute_fish_gifs)
            file = discord.File("pictures/" + chosen_picture, filename="image.gif")
        elif word in general_tourist_word:
            chosen_picture = random.choice(general_tourist_word)
            file = discord.File("pictures/" + chosen_picture, filename="image.gif")

        for key_word in word_phrase.split():
            if key_word in cat_word:
                chosen_picture = random.choice(cute_cats_gifs)
                file = discord.File("pictures/" + chosen_picture, filename="image.gif")
            elif key_word in general_tourist_word:
                chosen_picture = random.choice(general_tourist_png)
                file = discord.File("pictures/" + chosen_picture, filename="image.gif")
            elif key_word in food_word:
                chosen_picture = random.choice(chinese_food_png)
                file = discord.File("pictures/" + chosen_picture, filename="image.gif")
            elif key_word in fish_word:
                chosen_picture = random.choice(cute_fish_gifs)
                file = discord.File("pictures/" + chosen_picture, filename="image.gif")

    return file
