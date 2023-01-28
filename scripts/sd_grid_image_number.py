from modules import scripts, ui_components, script_callbacks
from modules.script_callbacks import ImageSaveParams
from modules.processing import Processed
from modules.shared import opts, OptionInfo, gr
from fonts.ttf import Roboto
from PIL import Image, ImageDraw, ImageColor, ImageFont, ImageFilter
import os, math
import matplotlib.font_manager

def adaptation(width, height, strength):
    diagonal = math.sqrt(width**2 + height**2)
    return int(diagonal / strength)

# Add option to settings
def on_ui_settings():
    section = ('numeric-grids', "Numeric Grids")
    font_options = matplotlib.font_manager.findSystemFonts()
    font_options.sort()
    font_options.insert(0, "Default")

    opts.add_option("sd_grid_add_image_number", OptionInfo(True, "Print an number of each image into the grid", section=section))
    opts.add_option("sd_grid_adaptive", OptionInfo(True, "Use adapted font size and distance for image number in grid", section=section))
    opts.add_option("sd_grid_num_distance", OptionInfo(8, "Custom distance of an image number from the corner of the grid", gr.Slider, {"minimum": 0, "maximum": 1024, "step": 1}, section=section))
    opts.add_option("sd_grid_font_size", OptionInfo(32, "Custom font size of the image number in grid", gr.Number, {"precision": 0}, section=section))
    opts.add_option("sd_grid_font", OptionInfo("Default", "Select a font of image number in the grid", gr.Dropdown, {"choices": font_options}, section=section))
    opts.add_option("sd_grid_text_color", OptionInfo("#ffffff", "Text color for image number in grid", ui_components.FormColorPicker, {}, section=section))
    opts.add_option("sd_grid_use_filename", OptionInfo(True, "Use the number in grid from its filename. Only works if 'Add number to filename when saving' is on. Practically useless with subdirectories.", section=section))
    opts.add_option("sd_grid_background_type", OptionInfo("Shadow", "Background type for image number in grid", gr.Radio, {"choices": ["Shadow", "Box"]}, section=section))
    opts.add_option("sd_grid_background_color", OptionInfo("#000000", "Background color for image number in grid", ui_components.FormColorPicker, {}, section=section))
    opts.add_option("sd_grid_background_transparency", OptionInfo(255, "Background transparency for image number in grid", gr.Slider, {"minimum": 0, "maximum": 255, "step": 1}, section=section))
    opts.add_option("sd_grid_start_number_at_one", OptionInfo(True, "Start counting the image number in grid from 1 instead of 0", section=section))
    opts.add_option("sd_grid_num_pos", OptionInfo("bottom left", "Position of an image number in grid", gr.Dropdown, {"choices": ["top left", "top right", "bottom left", "bottom right"]}, section=section))
script_callbacks.on_ui_settings(on_ui_settings)

# Insert individual image number, lower left corner, in front of a shadow text
def handle_image_grid(params : script_callbacks.ImageGridLoopParams):
    if opts.sd_grid_add_image_number and opts.samples_save:
        count = 1 if opts.sd_grid_start_number_at_one else 0

        for img in params.imgs:
            width, height = img.size
            grpos = opts.sd_grid_num_pos
            xpos, ypos = (0, 0) if grpos == "top left" else (width, 0) if grpos == "top right" else (0, height) if grpos == "bottom left" else (width, height) if grpos == "bottom right" else (0, height)

            if hasattr(img, "already_saved_as"):
                if opts.sd_grid_use_filename and opts.save_images_add_number:
                    img_filename = os.path.basename(img.already_saved_as)
                    img_filename_split = img_filename.split('-')
                    img_num_text = img_filename_split[0]
                else:
                    img_num_text = str(count)
                    count += 1
                    
                if img_num_text.isdigit():
                    img_num_draw = ImageDraw.Draw(img)
                    img_num_font = ImageFont.truetype(Roboto if opts.sd_grid_font == "Default" else opts.sd_grid_font, adaptation(width, height, 10) if opts.sd_grid_adaptive else opts.sd_grid_font_size)
                    img_num_distance = opts.sd_grid_num_distance if not opts.sd_grid_adaptive else adaptation(width, height, 80)
                    
                    img_num_width, img_num_height = img_num_draw.textsize(img_num_text, img_num_font)
                    offset_x, offset_y = img_num_font.getoffset(img_num_text)

                    img_num_x = xpos - offset_x + img_num_distance if grpos in ["top left", "bottom left"] else xpos - img_num_distance - img_num_width
                    img_num_y = ypos - offset_y + img_num_distance if grpos in ["top left", "top right"] else ypos - img_num_distance - img_num_height

                    fill = ImageColor.getrgb(opts.sd_grid_background_color) + (opts.sd_grid_background_transparency,)

                    if opts.sd_grid_background_type == "Shadow":
                        img_num_shdadow_distance = adaptation(width, height, 270)
                        img_num_shadow_x = xpos - offset_x + img_num_distance + img_num_shdadow_distance if grpos in ["top left", "bottom left"] else xpos - img_num_distance - img_num_width + img_num_shdadow_distance
                        img_num_shadow_y = ypos - offset_y + img_num_distance + img_num_shdadow_distance if grpos in ["top left", "top right"] else ypos - img_num_distance - img_num_height + img_num_shdadow_distance
                        img_num_shadow_text = Image.new("RGBA", img.size, (0,0,0,0))
                        img_num_shadow_draw = ImageDraw.Draw(img_num_shadow_text)
                        img_num_shadow_draw.text((img_num_shadow_x, img_num_shadow_y), img_num_text, font=img_num_font, fill=fill)
                        img_num_shadow_text = img_num_shadow_text.filter(ImageFilter.BLUR)
                        img.paste(img_num_shadow_text, (0,0), img_num_shadow_text)
                    elif opts.sd_grid_background_type == "Box":
                        bbox = img_num_draw.textbbox((img_num_x, img_num_y), img_num_text, font=img_num_font)
                        img_num_draw.rectangle(bbox, fill=fill)

                    img_num_draw.text((img_num_x, img_num_y), img_num_text, font=img_num_font, fill=opts.sd_grid_text_color)

# Initialize the image grid callback
script_callbacks.on_image_grid(handle_image_grid)