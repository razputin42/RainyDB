class RainyDatabase:
    def load_resources(self, path):

        self.item_table_widget.load_all("./item", "{}/{}/Items/".format(resource_path, self.version), item_cls)
        self.item_table_widget.fill_table()
        self.item_table_widget.define_filters(self.version)
        self.monster_table_widget.load_all("./monster", "{}/{}/Bestiary/".format(resource_path, self.version), monster_cls)
        self.monster_table_widget.fill_table()
        self.monster_table_widget.define_filters(self.version)
        self.spell_table_widget.load_all("./spell", "{}/{}/Spells/".format(resource_path, self.version), spell_cls)
        self.spell_table_widget.fill_table()
        self.spell_table_widget.define_filters(self.version)

    def load_all(self, s, dir, Class):
        self.dir = dir
        self.list = []
        for resource in os.listdir(dir):
            self.load_list(s, dir + resource, Class)
        self.list.sort(key=lambda x: x.name)
        for itt, entry in enumerate(self.list):
            entry.index = itt

    def load_specific(self, s, resource, Class):
        xml = ElementTree.parse(resource)
        root = xml.getroot()
        for itt, entry in enumerate(root.findall(s)):
            self.list.append(Class(entry, itt))
        self.list_dict[str(Class)] = self.list

