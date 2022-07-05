$(document).ready(function () {
    new Cleave('.ngay_ttrinh', {
        date: true,
        delimiter: '/',
        datePattern: ['d','m','Y']
    });

    new Cleave('.ngay_nhan_ttrinh', {
        date: true,
        delimiter: '/',
        datePattern: ['d','m','Y']
    });

    new Cleave('.ngay_cv_gia_han', {
        date: true,
        delimiter: '/',
        datePattern: ['d','m','Y']
    });
    
    new Cleave('.ngay_qd_tkt_dn', {
        date: true,
        delimiter: '/',
        datePattern: ['d','m','Y']
    });

    new Cleave('.thang_tktra', {
        date: true,
        delimiter: '/',
        datePattern: ['m','Y']
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
    $('#trinh_ky').val(localdate);
    $('.ngay_thang_1').val(dNow.getMonth()+1);
    $('.ngay_thang_2').val(dNow.getFullYear());
    
    $('.tktra').text($('#tktra_slt').val().trim());
    $('#tktra_slt').change (function () {
        var tktra = $('#tktra_slt').val().trim();
        $('.tktra').text(tktra);
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

    // $('tr[class=lq_cuc]')

    /* function leading_zero (str, max) {
    str = parseInt(str);
    return str < max ? ("0" + str) : str.toString();
    } */

    $(".mst").autocomplete({
        minLength: 3,
        //source: mst
        source: 'mst_autocomplete',
    });

    /* var i = 0;
    var tencb = []; var ngachcb = []; var cvdoan = [];
    $('#tbody tr').each(function() {
        tencb[i] = $(this).find(".cb_gioi_tinh").html() + ": " + $(this).find(".thanh_vien").val();
        ngachcb[i] = $(this).find(".ngach_cb").html(); 
        cvdoan[i] = $(this).find(".cv_doan").html(); 
        ++i;
    }); */
});