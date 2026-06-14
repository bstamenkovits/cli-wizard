import questionary


class Style:
    def __init__(self, color:str, weight:str = ""):
        self.color = color
        self.weight = weight

    @property
    def rich_style(self):
        return f"fg:{self.color} {self.weight}"

    @property
    def questionary_style(self):
        return f"fg:{self.color} {self.weight}"


class THEME:
    primary = Style(
        color="#ff9d00",
        weight="bold",
    )
    muted = Style(color="#6c7a89")


custom_questionary_style = questionary.Style([
    ('highlighted', f'fg:{THEME.primary.color} {THEME.primary.weight}'), # pointed-at choice in select and checkbox prompts
])