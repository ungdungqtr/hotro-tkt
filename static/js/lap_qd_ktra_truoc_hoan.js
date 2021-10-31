$(document).ready(function () {
    new Cleave('.ngay_ktra', {
        date: true,
        delimiter: '/',
        datePattern: ['d','m','Y']
    });
    new Cleave('.trinh_ky', {
        date: true,
        delimiter: '/',
        datePattern: ['d','m','Y']
    });
    new Cleave('.ngay_thang_1', {
        date: true,
        delimiter: '/',
        datePattern: ['m']
    });
    new Cleave('.ngay_thang_2', {
        date: true,
        delimiter: '/',
        datePattern: ['Y']
    });
    var dNow = new Date();
    var localdate= dNow.getDate() + '/' + (dNow.getMonth()+1) + '/' + dNow.getFullYear();
    $('.trinh_ky').val(localdate);
    $('.ngay_thang_1').val(dNow.getMonth()+1);
    $('.ngay_thang_2').val(dNow.getFullYear());
    // jQuery button click event to add a row.
    var rowIdx = 0; 
    $('#addBtn').on('click', function () {
    // Adding a row inside the tbody.
        $('#tbody').append(
            `<tr id="R${++rowIdx}">
                <td class="row-index">
                    <p class="cb_gioi_tinh"></p></td>
                <td class="row-index">
                    <input class="thanh_vien" name="thanh_vien" type="text" size="24" required></td>
                <td class="row-index">
                    <p class="ngach_cb"></p></td>
                <td class="row-index">
                    <p class="cv_doan" name="thanh_vien_cvu"></p></td>
                <td class="text-center">
                    <button class="btn btn-danger remove" 
                        type="button">Xóa</button></td>
            </tr>`);
        $('input.thanh_vien').autocomplete({
            minLength: 2,
            source : 'cb_ten_autocomplete',
        });
        // Thành viên đoàn kiểm tra
        $('.thanh_vien').each(function () {
            $(this).change(function () {
                var thanh_vien = $(this);
                $.ajax({
                    url: 'cb_thong_tin',
                    data: {'ten_cb' : $(this).val().trim()},
                    dataType: 'json',
                    success: function (data) {
                        if ($.isEmptyObject(data)) {
                            alert("Cán bộ không có tên trong danh sách\nVui lòng cập nhật");
                            thanh_vien.val('');   
                        } else {  
                            var tv =  thanh_vien.closest('tr');
                            tv.find('.cb_gioi_tinh').text(data.gioi_tinh); 
                            if (data.chuc_vu == "Công chức") {
                                tv.find('.ngach_cb').text(data.ngach_cb);   
                            } else {
                                tv.find('.ngach_cb').text(data.chuc_vu);   
                            }   
                            if (tv.attr('id') == 'R1') {
                                tv.find('.cv_doan').text("Trưởng đoàn"); 
                            } else {
                                tv.find('.cv_doan').text("Thành viên"); 
                            }
                        }
                    }
                });
            });
        });

        
    });

    $('#tbody').on('click', '.remove', function () {    
        // Getting all the rows next to the 
        // row containing the clicked button
        var child = $(this).closest('tr').nextAll();

        // Iterating across all the rows 
        // obtained to change the index
        child.each(function () {
            
            // Getting <tr> id.
            var id = $(this).attr('id');

            // Getting the <p> inside the .row-index class.
            //var idx = $(this).children('.row-index').children('p');

            // Gets the row number from <tr> id.
            var dig = parseInt(id.substring(1));

            // Modifying row index.
            //idx.html(`Row ${dig - 1}`);

            // Modifying row id.
            $(this).attr('id', `R${dig - 1}`);
        });

        // Removing the current row.
        $(this).closest('tr').remove();

        // Decreasing the total number of rows by 1.
        rowIdx--;
    });
    // Hiển thị thông tin nnt
    $('.mst').change (function () {
        var mst = $('.mst').val().trim();
        $.ajax({
            url: 'nnt_thong_tin',
            data: {'mst' : mst},
            dataType: 'json',
            success: function (data) {
                if($.isEmptyObject(data)) {
                    alert("Người nộp thuế không tồn tại trong danh bạ\nVui lòng cập nhật");
                    $('.mst').val('');    
                } else {               
                    $('.ten_dv').text(data.ten_nnt);
                    $('.dia_chi').text("Địa chỉ: " + data.dia_chi);
                }
            } 
        });
    });  

    /* function leading_zero (str, max) {
    str = parseInt(str);
    return str < max ? ("0" + str) : str.toString();
    } */

    $(".mst").autocomplete({
        minLength: 3,
        //source: mst
        source: 'mst_autocomplete',
    });
});