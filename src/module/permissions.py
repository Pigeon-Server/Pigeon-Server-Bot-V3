class Mcsm:
    """
    关于mcsm面板的权限节点
    """

    class Update:
        Common: str = "Mcsm.Update.Common"
        Force: str = "Mcsm.Update.Force"

    Check: str = "Mcsm.Check"
    List: str = "Mcsm.List"
    Rename: str = "Mcsm.Rename"
    Stop: str = "Mcsm.Stop"
    Kill: str = "Mcsm.Kill"
    Start: str = "Mcsm.Start"
    Restart: str = "Mcsm.Restart"
    Command: str = "Mcsm.Command"

    @staticmethod
    def get_all_permission_node() -> list:
        return [Mcsm.Command, Mcsm.Kill, Mcsm.Start, Mcsm.Stop, Mcsm.Restart,
                Mcsm.Check, Mcsm.List, Mcsm.Rename, Mcsm.Update.Force, Mcsm.Update.Common]


class Permission:
    """
    关于权限系统自身的权限节点
    """

    class Player:
        Give: str = "Permission.Player.Give"
        Remove: str = "Permission.Player.Remove"
        Check: str = "Permission.Player.Check"
        List: str = "Permission.Player.List"
        Clone: str = "Permission.Player.Clone"
        Del: str = "Permission.Player.Del"
        Info: str = "Permission.Player.Info"
        Create: str = "Permission.Player.Create"

        class Parent:
            Add: str = "Permission.Player.Inherit.Add"
            Del: str = "Permission.Player.Inherit.Del"
            Set: str = "Permission.Player.Inherit.Set"

    class Group:
        Give: str = "Permission.Group.Give"
        Remove: str = "Permission.Group.Remove"
        List: str = "Permission.Group.List"
        Clone: str = "Permission.Group.Clone"
        Del: str = "Permission.Group.Del"
        Info: str = "Permission.Group.Info"
        Check: str = "Permission.Group.Check"
        Create: str = "Permission.Group.Create"

        class Parent:
            Add: str = "Permission.Group.Inherit.Add"
            Del: str = "Permission.Group.Inherit.Del"

    class Reload:
        Common: str = "Permission.Group.Reload.Common"
        Force: str = "Permission.Group.Reload.Force"

    ShowList: str = "Permission.List"

    @staticmethod
    def get_all_permission_node() -> list:
        return [Permission.Player.Check, Permission.Player.Clone, Permission.Player.Give, Permission.Player.Remove,
                Permission.Player.List, Permission.Player.Parent.Del, Permission.Player.Parent.Add,
                Permission.Player.Del, Permission.Player.Info,
                Permission.Player.Create, Permission.Player.Parent.Set,
                Permission.Group.List, Permission.Group.Clone, Permission.Group.Remove, Permission.Group.Give,
                Permission.Group.Info,
                Permission.Group.Del, Permission.Group.Parent.Add, Permission.Group.Parent.Del,
                Permission.Group.Check,
                Permission.Reload.Common, Permission.Reload.Force, Permission.Group.Create,
                Permission.ShowList]


class Whitelist:
    """
    白名单权限节点
    """
    Apply: str = "Whitelist.Apply"
    Change: str = "Whitelist.Change"
    Agree: str = "Whitelist.Agree"
    AgreeALL: str = "Whitelist.AgreeALL"
    Refuse: str = "Whitelist.Refuse"

    class List:
        Wait: str = "Whitelist.List.Wait"

    @staticmethod
    def get_all_permission_node() -> list:
        return [Whitelist.Apply, Whitelist.Agree, Whitelist.AgreeALL, Whitelist.Change, Whitelist.Refuse,
                Whitelist.List.Wait]


class Blacklist:
    """
    黑名单权限节点
    """
    List: str = "Blacklist.List"
    Check: str = "Blacklist.Check"
    Add: str = "Blacklist.Add"
    Remove: str = "Blacklist.Remove"

    @staticmethod
    def get_all_permission_node() -> list:
        return [Blacklist.List, Blacklist.Check, Blacklist.Add, Blacklist.Remove]


class Token:
    """
    秘钥权限节点
    """
    Lock: str = "Token.Lock"
    Unlock: str = "Token.Unlock"
    Check: str = "Token.Check"

    @staticmethod
    def get_all_permission_node() -> list:
        return [Token.Lock, Token.Unlock, Token.Check]


class Question:
    """
    问答权限节点
    """
    Shutup: str = "Question.Shutup"
    GetAnswer: str = "Question.GetAnswer"

    @staticmethod
    def get_all_permission_node() -> list:
        return [Question.GetAnswer, Question.Shutup]
