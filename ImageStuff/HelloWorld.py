import json
import PIL
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

stuff = [[" ",       "500",    "2K",     "5K",      "6K",      "10K",     "60'"],
         ["SB",      "1:32.6", "6:45.4", "17:35.2", "21:31.1", "37:14.1", "16056"],
		 ["PB",      "1:29.0", "6:32.0", "17:12.1", "20:50.9", "34:58.3", "16690"],
		 ["PB Year", "2007",   "2009",   "2008",    "2009",    "2009" ,   "2008" ]]
		 

		 
class Cell:
	def __init__(self, text):
		self.label = text
		
	def __str__(self):
		return self.label
		
	def measure(self, drawing_context, font):
		w, h = drawing_context.textsize(self.label, font)
		self.text_width = w
		self.text_height = h
		
	def get_text_dim(self):
		return (self.text_width + 10, self.text_height + 6)

	def set_cell_width(self, width):
		self.cell_width = width
		
	def set_cell_height(self, height):
		self.cell_height = height
		
	def get_cell_dim(self):
		return (self.cell_width, self.cell_height)
		
	def draw(self, drawing_context, font, pos):
		drawing_context.text((pos[0]+(self.cell_width-self.text_width)/2, pos[1]+(self.cell_height-self.text_height)/2 - 1), self.label, (0, 0, 0), font)
		# top-left to bottom-left
		drawing_context.line((pos[0], pos[1], pos[0], pos[1]+self.cell_height), fill = 50, width = 1)
		# top-left to top-right
		drawing_context.line((pos[0], pos[1], pos[0]+self.cell_width-1, pos[1]), fill = 120, width = 1)
		# bottom-right to bottom-left
		drawing_context.line((pos[0]+self.cell_width-1, pos[1]+self.cell_height-1, pos[0], pos[1]+self.cell_height-1), fill = 190, width = 1)
		# bottom-right to top-right
		drawing_context.line((pos[0]+self.cell_width-1, pos[1], pos[0]+self.cell_width-1, pos[1]+self.cell_height), fill = 255, width = 1)
		
class Grid:
	def __init__(self, r, c):
		self.row_count = r
		self.col_count = c
		self.grid = []
		for row_index in range(self.row_count):
			self.grid.append(list(range(self.col_count)))
	
	def __str__(self):
		return ""
		
	def add_thing(self, r, c, thing):
		self.grid[r][c] = thing
		
	def get_row(self, r):
		return self.grid[r]
		
	def get_col(self, c):
		return [self.grid[r][c] for r in range(self.row_count)]
		
	def get_rows(self):
		return [self.get_row(r) for r in range(self.row_count)]
		
	def get_cols(self):
		return [self.get_col(c) for c in range(self.col_count)]
		
	def get_all(self):
		return [self.grid[r][c] for r in range(self.row_count) for c in range(self.col_count)]
		
	

class Table:
	def __init__(self, r, c):
		self.grid = Grid(r, c)
		self.font = PIL.ImageFont.truetype("arial.ttf", 10)
		
	def __str__(self):
		return str(self.grid)
	
	def add_cell(self, row_index, column_index, cell):
		self.grid.add_thing(row_index, column_index, cell)
		
	def set_cell_dimensions(self):
		image = PIL.Image.new("RGBA", (100, 100), (255, 255, 255))
		drawing_context = PIL.ImageDraw.Draw(image)
		for cell in self.grid.get_all():
			cell.measure(drawing_context, self.font)
			
	def set_cell_sizes(self):
		for row in self.grid.get_rows():
			row_max_height = 0
			for cell in row:
				if cell.get_text_dim()[1] > row_max_height:
						row_max_height = cell.get_text_dim()[1]
			for cell in row:
				cell.set_cell_height(row_max_height)
		for col in self.grid.get_cols():
			col_max_width = 0
			for cell in col:
				if cell.get_text_dim()[0] > col_max_width:
					col_max_width = cell.get_text_dim()[0]
			for cell in col:
				cell.set_cell_width(col_max_width)
	
	def get_table_dim(self):
		row = self.grid.get_row(0)
		col = self.grid.get_col(0)
		width = 0
		for cell in row:
			width += cell.get_cell_dim()[0]
		height = 0
		for cell in col:
			height += cell.get_cell_dim()[1]
		return (width+2, height+2)
	
	def get_image(self):
		table_dim = self.get_table_dim()
		image = PIL.Image.new("RGBA", table_dim, (255, 255, 255))
		drawing_context = PIL.ImageDraw.Draw(image)
		top = 1
		for row in self.grid.get_rows():
			left = 1
			height = 0
			for cell in row:
				print (left, top)
				cell.draw(drawing_context, self.font, (left, top))
				cell_dim = cell.get_cell_dim()
				left += cell_dim[0]
				height = cell_dim[1]
			top += height
		
		# top-left to bottom-left
		drawing_context.line((0, 0, 0, table_dim[1]), fill = 50, width = 1)
		# top-left to top-right
		drawing_context.line((0, 0, table_dim[0], 0), fill = 120, width = 1)
		# bottom-right to bottom-left
		drawing_context.line((table_dim[0], table_dim[1]-1, 0, table_dim[1]-1), fill = 190, width = 1)
		# bottom-right to top-right
		drawing_context.line((table_dim[0]-1, 0, table_dim[0]-1, table_dim[1]), fill = 255, width = 1)
		
		return image
	
table = Table(4,7)

row_index = 0
for row in stuff:
	column_index = 0
	for column in row:
		cell = Cell(column)
		table.add_cell(row_index, column_index, cell)
		column_index += 1
	row_index += 1	

table.set_cell_dimensions()
table.set_cell_sizes()

image = table.get_image()

image.save("x.jpg")

