class RestRoutes(object):
    ping = "ping"
    common_search = "conans/search"
    common_authenticate = "users/authenticate"
    oauth_authenticate = "users/token"
    common_check_credentials = "users/check_credentials"

    def __init__(self):
        self.base = 'conans'

    @property
    def recipe(self):
        return self.base + '/{name}/{version}/{username}/{channel}'

    @property
    def recipe_latest(self):
        return f'{self.recipe}/latest'

    @property
    def recipe_revision(self):
        return '%s/revisions/{revision}' % self.recipe

    @property
    def recipe_revision_files(self):
        return f'{self.recipe_revision}/files'

    @property
    def recipe_revisions(self):
        return f'{self.recipe}/revisions'

    @property
    def recipe_revision_file(self):
        return '%s/files/{path}' % self.recipe_revision

    @property
    def packages(self):
        return f'{self.recipe}/packages'

    @property
    def packages_revision(self):
        return f'{self.recipe_revision}/packages'

    @property
    def package(self):
        return '%s/{package_id}' % self.packages

    @property
    def package_files(self):
        return f'{self.package}/files'

    @property
    def package_recipe_revision(self):
        """Route for a package specifying the recipe revision but not the package revision"""
        return '%s/{package_id}' % self.packages_revision

    @property
    def package_revisions(self):
        return f'{self.package_recipe_revision}/revisions'

    @property
    def package_revision(self):
        return '%s/{p_revision}' % self.package_revisions

    @property
    def package_revision_files(self):
        return f'{self.package_revision}/files'

    @property
    def package_revision_latest(self):
        return f'{self.package_recipe_revision}/latest'

    @property
    def package_revision_file(self):
        return '%s/files/{path}' % self.package_revision

    @property
    def common_search_packages(self):
        return f"{self.recipe}/search"

    @property
    def common_search_packages_revision(self):
        return f"{self.recipe_revision}/search"
