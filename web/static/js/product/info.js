;
var member_order_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        var that = this;

        $(".pay").click(function () {
            that.ops('pay', $(this).attr("data"));
        });

        $(".cancel").click(function () {
            that.ops('cancel', $(this).attr("data"));
        });
    },
    ops: function (action, id) {
        var callback = {
            'ok': function () {
                $.ajax({
                    url: common_ops.buildUrl("/member/order_ops"),
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
        common_ops.confirm((action == "pay" ? "确定已付款了吗？" : "确定取消吗？"), callback)
    }
};

$(document).ready(function () {
    member_order_ops.init()
});