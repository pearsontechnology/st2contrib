from lib import action


class VaultCreateTokenAction(action.VaultBaseAction):
    def run(self, id=None, policies=None, meta=None, no_parent=False, display_name=None, num_uses=None, no_default_policy=False, ttl=None, orphan=False, wrap_ttl=None):
        return self.vault.create_token(id, policies, meta, no_parent, display_name, num_uses, no_default_policy, ttl, orphan, wrap_ttl)

