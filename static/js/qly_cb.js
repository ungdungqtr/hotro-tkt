$(document).ready(function () {
    // Thêm mới cán bộ
    $("form#addUser").submit(function (e) { 
        e.preventDefault();
        var gioi_tinh_input = $('select[name=gioi_tinh]').val();
        var ten_cb_input = $('input[name=ten_cb]').val().trim();
        var chuc_vu_input = $('select[name=chuc_vu]').val();
        if (gioi_tinh_input && ten_cb_input && chuc_vu_input) {
            $.ajax({
                url: "them_moi_cb",
                data: {
                    'gioi_tinh' : gioi_tinh_input,
                    'ten_cb' : ten_cb_input,
                    'chuc_vu' : chuc_vu_input
                },
                dataType: "json",
                success: function (data) {
                    if (data.user) {
                        appendToUsrTable(data.user);
                    }
                    $('form#addUser').trigger("reset");
                    return false;   
                }
            });
        } else {
            alert("Yêu cầu điền đầy đủ thông tin cán bộ");
        }
    });

    //Thêm dòng vào bảng
    function appendToUsrTable(user) {
        $("#userTable > tbody:last-child").append(`
            <tr id="user-${user.id}">
                <td class="userGtinh userData" name="gioi_tinh">${user.gioi_tinh}</td>
                <td class="userTen userData" name="ten_cb">${user.ten_cb}</td>
                <td class="userCvu userData" name="chuc_vu">${user.chuc_vu}</td>
                <td align="center">
                <button type="button" class="btn btn-success btn-sm form-control update_cb" value="{{user.id}}" 
                        data-toggle="modal" data-target="#UpdateModal">
                        <i class="bi bi-pencil-fill"></i>
                    </button>
                </td>
                <td align="center">
                    <button class="btn btn-danger form-control btn-smxoa_cb" value="{{user.id}}">
                        <i class="bi bi-trash-fill"></i>
                    </button>
                </td>
            </tr>
        `);
    }

    // Xóa dữ liệu
    $('.xoa_cb').click(function (e) { 
        e.preventDefault();
        var id = $(this).attr('value');
        var action = confirm("Bạn có chắc chắn muốn xóa thông tin cán bộ này?");
        if (action != false) {
            $.ajax({
                url: "xoa_cb",
                data: {'id' : id},
                dataType: "json",
                success: function (data) {
                    if (data.delete) {
                        $('#userTable #user-' + id).remove();
                    }
                }
            }); 
        }       
    });
    //Lấy thông tin từ bảng đưa vào Modal
    $('.update_cb').click(function (e) { 
        e.preventDefault();
        var id = $(this).attr('value');
        if (id) {
            tr_id = '#user-' + id;
            gioi_tinh = $(tr_id).find('.userGtinh').text();
            ten_cb = $(tr_id).find('.userTen').text();
            chuc_vu = $(tr_id).find('.userCvu').text();
            $('#form-id').val(id);
            // $('#form-gtinh option[value=${gioi_tinh}]').attr("selected",true);
            $('#form-gtinh').val(gioi_tinh);
            $('#form-ten').val(ten_cb);
            $('#form-cvu').val(chuc_vu);
        }
    });
    //Cập nhật thông tin cán bộ
    $('form#updateUser').submit(function () { 
        // e.preventDefault();
        var idInput = $('input[name="formId"]').val();
        var gtinhInput = $('select[name="formGtinh"]').val();
        var tenInput = $('input[name="formTen"]').val().trim();
        var cvuInput = $('select[name="formCvu"]').val();

        if (gtinhInput && tenInput && cvuInput) {
            $.ajax({
                url: "cap_nhat_thong_tin",
                data: {
                    'id': idInput,
                    'gioi_tinh': gtinhInput,
                    'ten_cb': tenInput,
                    'chuc_vu': cvuInput,
                },
                dataType: "json",
                success: function (data) {
                    if (data.user) {
                        updateToUserTable(data.user);
                    }
                }
            });
        } else {
            alert("Vui lòng điền đầy đủ thông tin");
        }
        $('form#updateUser').trigger("reset");
        $('#UpdateModal').modal('hide');
        return false;
    });
    
    //Cập nhật lại bảng
    function updateToUserTable(user) {
        $('#userTable #user-' + user.id).children(".userData").each(function() {
            var attr = $(this).attr("name");
            if (attr == "gioi_tinh") {
                $(this).text(user.gioi_tinh);
            } else if (attr == "ten_cb") {
                $(this).text(user.ten_cb);
            } else {
                $(this).text(user.chuc_vu);
            }
        }); 
    }
});