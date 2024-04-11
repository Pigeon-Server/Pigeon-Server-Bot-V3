from src.element.tree import Tree


class Mcsm:
    """
    关于mcsm面板的权限节点
    """

    class Update:
        Common: Tree = Tree("Mcsm.Update.Common")
        Force: Tree = Tree("Mcsm.Update.Force")
        instance: Tree = Tree("Mcsm.Update.*").insert(Common).insert(Force)

    Check: Tree = Tree("Mcsm.Check")
    List: Tree = Tree("Mcsm.List")
    Rename: Tree = Tree("Mcsm.Rename")
    Stop: Tree = Tree("Mcsm.Stop")
    Kill: Tree = Tree("Mcsm.Kill")
    Start: Tree = Tree("Mcsm.Start")
    Restart: Tree = Tree("Mcsm.Restart")
    Command: Tree = Tree("Mcsm.Command")

    instance: Tree = (Tree("Mcsm.*")
                      .insert(Update.instance)
                      .insert(Check)
                      .insert(List)
                      .insert(Rename)
                      .insert(Stop)
                      .insert(Kill)
                      .insert(Start)
                      .insert(Restart)
                      .insert(Command))


class Permission:
    """
    关于权限系统自身的权限节点
    """

    class Player:
        class Parent:
            Add: Tree = Tree("Permission.Player.Parent.Add")
            Del: Tree = Tree("Permission.Player.Parent.Del")
            Set: Tree = Tree("Permission.Player.Parent.Set")
            instance: Tree = (Tree("Permission.Player.Parent.*")
                              .insert(Add)
                              .insert(Del)
                              .insert(Set))

        Give: Tree = Tree("Permission.Player.Give")
        Remove: Tree = Tree("Permission.Player.Remove")
        Check: Tree = Tree("Permission.Player.Check")
        List: Tree = Tree("Permission.Player.List")
        Clone: Tree = Tree("Permission.Player.Clone")
        Del: Tree = Tree("Permission.Player.Del")
        Info: Tree = Tree("Permission.Player.Info")
        Create: Tree = Tree("Permission.Player.Create")
        instance: Tree = (Tree("Permission.Player.*")
                          .insert(Parent.instance)
                          .insert(Give)
                          .insert(Remove)
                          .insert(Check)
                          .insert(List)
                          .insert(Clone)
                          .insert(Del)
                          .insert(Info)
                          .insert(Create))

    class Group:
        class Parent:
            Add: Tree = Tree("Permission.Group.Parent.Add")
            Del: Tree = Tree("Permission.Group.Parent.Del")
            instance: Tree = (Tree("Permission.Group.Parent.*")
                              .insert(Add)
                              .insert(Del))

        class Reload:
            Common: Tree = Tree("Permission.Group.Reload.Common")
            Force: Tree = Tree("Permission.Group.Reload.Force")
            instance: Tree = (Tree("Permission.Group.Reload.*")
                              .insert(Common)
                              .insert(Force))

        Give: Tree = Tree("Permission.Group.Give")
        Remove: Tree = Tree("Permission.Group.Remove")
        List: Tree = Tree("Permission.Group.List")
        Clone: Tree = Tree("Permission.Group.Clone")
        Del: Tree = Tree("Permission.Group.Del")
        Info: Tree = Tree("Permission.Group.Info")
        Check: Tree = Tree("Permission.Group.Check")
        Create: Tree = Tree("Permission.Group.Create")

        instance: Tree = (Tree("Permission.Group.*")
                          .insert(Parent.instance)
                          .insert(Reload.instance)
                          .insert(Give)
                          .insert(Remove)
                          .insert(List)
                          .insert(Clone)
                          .insert(Del)
                          .insert(Info)
                          .insert(Check)
                          .insert(Create))

    ShowList: Tree = Tree("Permission.List")

    instance: Tree = (Tree("Permission.*")
                      .insert(Player.instance)
                      .insert(Group.instance)
                      .insert(ShowList))


class Root:
    instance: Tree = (Tree("*.*")
                      .insert(Mcsm.instance)
                      .insert(Permission.instance))
