from auth import RoleHierarchyRepository, RoleHierarchy, init


# Write test cases here


def test_role_hierarchy_repository():
    repo = RoleHierarchyRepository()
    role1 = RoleHierarchy("Role1")
    role2 = RoleHierarchy("Role2")

    repo.roles["Role1"] = role1
    repo.roles["Role2"] = role2

    assert repo.get_role_hierarchy("Role1") == role1
    assert repo.get_role_hierarchy("Role2") == role2
    assert repo.get_all_roles() == {"Role1": role1, "Role2": role2}


def test_role_hierarchy():
    role_hierarhcy_spec = init()
    admin = role_hierarhcy_spec.create_role("admin")
    contributor = role_hierarhcy_spec.create_role("contributor")
    reader = role_hierarhcy_spec.create_role("reader")
    admin.provide_implicit_permissions(contributor, reader)
    contributor.provide_implicit_permissions(reader)
    reader.provide_implicit_permissions(None)
    role_repo = RoleHierarchyRepository()
    role_hierarchy = role_repo.get_role_hierarchy("admin")
    # check that implicit permissions contains contributor and reader
    assert role_hierarchy.implicit_permissions == [contributor, reader]
    assert contributor.implicit_permissions == [reader]
