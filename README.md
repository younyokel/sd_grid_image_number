# Stable Diffusion extension: Add the image's number to its picture in the grid

A custom extension for [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) to add the image's number to its picture in the grid.

Supports number positioning, counting from the beginning of the grid or by filename, custom colors, shadow or box background mode.

After choosing a new grid option in the settings:

<img src="images/settings.jpg"/>

the individual image numbers are added on the grid:

<img src="images/grid-1517-123-stickman.png"/>

<img src="images/xy_grid-0137-123-stickman.png"/>

This should make identifying the images, especially in larger batches, much easier.

## Installation

The extension can be installed directly from within the **Extensions** tab within the Webui.

You can also install it manually by running the following command from within the webui directory:

	git clone https://github.com/younyokel/sd_grid_image_number extensions/sd_grid_image_number
