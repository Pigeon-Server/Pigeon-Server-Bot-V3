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
    Status: Tree = Tree("Mcsm.Status")
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
                      .insert(Status)
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

        Add: Tree = Tree("Permission.Player.Add")
        Remove: Tree = Tree("Permission.Player.Remove")
        Check: Tree = Tree("Permission.Player.Check")
        List: Tree = Tree("Permission.Player.List")
        Clone: Tree = Tree("Permission.Player.Clone")
        Del: Tree = Tree("Permission.Player.Del")
        Info: Tree = Tree("Permission.Player.Info")
        Create: Tree = Tree("Permission.Player.Create")
        instance: Tree = (Tree("Permission.Player.*")
                          .insert(Parent.instance)
                          .insert(Add)
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

        Add: Tree = Tree("Permission.Group.Add")
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
                          .insert(Add)
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


class Whitelist:
    Add: Tree = Tree("Whitelist.Add")
    Del: Tree = Tree("Whitelist.Del")
    instance: Tree = Tree("Whitelist.*").insert(Add).insert(Del)


class ServerList:
    Add: Tree = Tree("ServerList.Add")
    Del: Tree = Tree("ServerList.Del")
    Enable: Tree = Tree("ServerList.Enable")
    Disable: Tree = Tree("ServerList.Disable")
    List: Tree = Tree("ServerList.List")
    Rename: Tree = Tree("ServerList.Rename")
    Modify: Tree = Tree("ServerList.Modify")
    Reload: Tree = Tree("ServerList.Reload")
    Weight: Tree = Tree("ServerList.Weight")
    instance: Tree = (Tree("ServerList.*")
                      .insert(Add)
                      .insert(Del)
                      .insert(Enable)
                      .insert(Disable)
                      .insert(List)
                      .insert(Rename)
                      .insert(Modify)
                      .insert(Reload)
                      .insert(Weight))


class BlockWords:
    Add: Tree = Tree("BlockWords.Add")
    Del: Tree = Tree("BlockWords.Del")
    Reload: Tree = Tree("BlockWords.Reload")
    List: Tree = Tree("BlockWords.List")
    instance: Tree = (Tree("BlockWords.*")
                      .insert(Add)
                      .insert(Del)
                      .insert(Reload)
                      .insert(List))


class Other:
    Reboot: Tree = Tree("Other.Reboot")
    Word: Tree = Tree("Other.Word")
    Status: Tree = Tree("Other.Status")
    instance: Tree = Tree("Other.*").insert(Reboot).insert(Word).insert(Status)


class Root:
    instance: Tree = (Tree("*.*")
                      .insert(Mcsm.instance)
                      .insert(Permission.instance)
                      .insert(Whitelist.instance)
                      .insert(ServerList.instance)
                      .insert(Other.instance))
