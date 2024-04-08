from src.element.tree import BinaryTree


class Mcsm:
    """
    关于mcsm面板的权限节点
    """

    class Update:
        Common: BinaryTree = BinaryTree("Mcsm.Update.Common")
        Force: BinaryTree = BinaryTree("Mcsm.Update.Force")
        instance: BinaryTree = BinaryTree("Mcsm.Update.*").insert(Common).insert(Force)

    Check: BinaryTree = BinaryTree("Mcsm.Check")
    List: BinaryTree = BinaryTree("Mcsm.List")
    Rename: BinaryTree = BinaryTree("Mcsm.Rename")
    Stop: BinaryTree = BinaryTree("Mcsm.Stop")
    Kill: BinaryTree = BinaryTree("Mcsm.Kill")
    Start: BinaryTree = BinaryTree("Mcsm.Start")
    Restart: BinaryTree = BinaryTree("Mcsm.Restart")
    Command: BinaryTree = BinaryTree("Mcsm.Command")

    instance: BinaryTree = (BinaryTree("Mcsm.*")
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
            Add: BinaryTree = BinaryTree("Permission.Player.Parent.Add")
            Del: BinaryTree = BinaryTree("Permission.Player.Parent.Del")
            Set: BinaryTree = BinaryTree("Permission.Player.Parent.Set")
            instance: BinaryTree = (BinaryTree("Permission.Player.Parent.*")
                                    .insert(Add)
                                    .insert(Del)
                                    .insert(Set))

        Give: BinaryTree = BinaryTree("Permission.Player.Give")
        Remove: BinaryTree = BinaryTree("Permission.Player.Remove")
        Check: BinaryTree = BinaryTree("Permission.Player.Check")
        List: BinaryTree = BinaryTree("Permission.Player.List")
        Clone: BinaryTree = BinaryTree("Permission.Player.Clone")
        Del: BinaryTree = BinaryTree("Permission.Player.Del")
        Info: BinaryTree = BinaryTree("Permission.Player.Info")
        Create: BinaryTree = BinaryTree("Permission.Player.Create")
        instance: BinaryTree = (BinaryTree("Permission.Player.*")
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
            Add: BinaryTree = BinaryTree("Permission.Group.Parent.Add")
            Del: BinaryTree = BinaryTree("Permission.Group.Parent.Del")
            instance: BinaryTree = (BinaryTree("Permission.Group.Parent.*")
                                    .insert(Add)
                                    .insert(Del))

        class Reload:
            Common: BinaryTree = BinaryTree("Permission.Group.Reload.Common")
            Force: BinaryTree = BinaryTree("Permission.Group.Reload.Force")
            instance: BinaryTree = (BinaryTree("Permission.Group.Reload.*")
                                    .insert(Common)
                                    .insert(Force))

        Give: BinaryTree = BinaryTree("Permission.Group.Give")
        Remove: BinaryTree = BinaryTree("Permission.Group.Remove")
        List: BinaryTree = BinaryTree("Permission.Group.List")
        Clone: BinaryTree = BinaryTree("Permission.Group.Clone")
        Del: BinaryTree = BinaryTree("Permission.Group.Del")
        Info: BinaryTree = BinaryTree("Permission.Group.Info")
        Check: BinaryTree = BinaryTree("Permission.Group.Check")
        Create: BinaryTree = BinaryTree("Permission.Group.Create")

        instance: BinaryTree = (BinaryTree("Permission.Group.*")
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

    ShowList: BinaryTree = BinaryTree("Permission.List")

    instance: BinaryTree = (BinaryTree("Permission.*")
                            .insert(Player.instance)
                            .insert(Group.instance)
                            .insert(ShowList))


class Root:
    instance: BinaryTree = (BinaryTree("*.*")
                            .insert(Mcsm.instance)
                            .insert(Permission.instance))
