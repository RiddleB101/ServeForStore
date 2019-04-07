;
var account_set_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        var that = this;
        $(".wrap_search .search").click(function () {
            $(".wrap_search .search").submit()
        });

        $(".remove").click(function () {
            that.ops('remove', $(this).attr("data"));
        });

        $(".recovery").click(function () {
            that.ops('recovery', $(this).attr("data"));
        });
    },
    ops: function (action, id) {
        var callback = {
            'ok': function () {
                $.ajax({
                    url: common_ops.buildUrl("/account/ops"),
                    type: "POST",
                    data: {
                        action: action,
                        id: id
                    },
                    dataType: "json",
                    success: function (res) {
                        var callback = null;
                        if (res.code === 200) {
                            callback = function () {
                                window.location.href = window.location.href;
                            }
                        }
                        common_ops.alert(res.msg, callback)
                    }
                })
            },
            'cancel': null
        };
        common_ops.confirm((action == "remove" ? "确定删除吗？" : "确定恢复吗？"), callback)

    }
};

$(document).ready(function () {
    account_set_ops.init()
});