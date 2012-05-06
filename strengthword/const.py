#!/usr/bin/python
# -*- coding: utf-8 -*-

wordview_common_js = u'''
(function() {

    // 删除「生词本」
    var new_word_node = document.querySelector('span.new_word');
    new_word_node.parentElement.removeChild(new_word_node);

    // 链接可点击
    var links = document.querySelectorAll('a.explain');
    var i, link;
    for (i = 0; i < links.length; i += 1) {
        link = links[i];
        link.href = location.href.replace(/word=.+?&/, 'word=' + link.textContent + '&');
    }

}());
'''

wordview_js = u'''
(function() {

    // 添加查询的单词
    var word_node = document.createElement('span');
    word_node.textContent = '%(word)s';
    word_node.style.cssText = 'color: black; float: left; font-size: 24px; line-height: 24px; margin-right: 10px;';
    var place_node = document.querySelector('#dict_main .eg');
    place_node.parentNode.insertBefore(word_node, place_node);

    // 双击选择跳转
    document.addEventListener('dblclick', function() {
        var selected = document.getSelection().toString().trim();
        if (selected == '') {
            return;
        }
        location.href = location.href.replace(/word=.+?&/, 'word=' + selected + '&');
    })

}());
'''

popup_wordview_js = u'''
(function() {

    // 添加查询的单词以及「详细」链接
    var word_node = document.createElement('span');
    word_node.textContent = '%(word)s';
    word_node.style.cssText = 'color: black; font-size: 13px; line-height: 13px';
    var detail_link = document.createElement('a');
    detail_link.href = '#detail';
    detail_link.textContent = '详细 >>';
    detail_link.style.cssText = 'float: right; font-size: 13px; text-decoration: none;';

    var title_node = document.createElement('div');
    title_node.style.marginBottom = '5px';
    title_node.appendChild(word_node);
    title_node.appendChild(detail_link);

    var place_node = document.querySelector('#dict_main .eg');
    place_node.parentNode.insertBefore(title_node, place_node);

}());
'''

sentenceview_js = u'''
(function() {

    // 宽度修复
    var node = document.getElementById('right');
    //node.style.width = '100%';

    // 双击选择跳转
    document.addEventListener('dblclick', function() {
        var selected = document.getSelection().toString().trim();
        if (selected == '') {
            return;
        }
        location.href = location.href.replace(/&s=.+$/, '&s=' + selected);
    })

}());
'''

wordview_not_found_html = u'''
<!DOCTYPE HTML>
<html>
<head>
	<meta charset="UTF-8"> <title>not found</title>
    <style type="text/css">
        body {
            font-size: 13px;
            margin: 16px;
        }
    </style>
</head>
<body>

<p>当前词典中暂无与「%(word)s」相符的解释</p>

<strong>建议您：<strong>

<p>1. 去爱词霸网站<a href="http://bbs.iciba.com/forum.php?mod=forumdisplay&fid=52">发帖求助</a>；</p>

<p>2. 搜索<a href="http://www.sogou.com/sogou?query=%(word)s">%(word)s</a>。</p>

</body>
</html>
'''

popup_wordview_too_long_html = u'''
<!DOCTYPE HTML>
<html>
<head>
	<meta charset="UTF-8">
	<title>not found</title>
    <style type="text/css">
        body {
            font-size: 13px;
        }
    </style>
</head>
<body>

<p>选择文本过长，超出 %(exceed_count)s 个字符，忽略本次取词。</p>

</body>
</html>
'''

sentenceview_not_found_html = u'''
<!DOCTYPE HTML>
<html>
<head>
	<meta charset="UTF-8">
	<title>not found</title>
    <style type="text/css">
        body {
            font-size: 13px;
            margin: 16px;
        }
    </style>
</head>
<body>

<p>很抱歉，暂无与「%(word)s」 相关的例句。</p>

<strong>建议您：<strong>

<p>1. 检查输入的文字是否有误；</p>

<p>2. 去掉可能不必要的字词，如「的」、「什么」等；</p>

<p>3. 搜索<a href="http://www.sogou.com/sogou?query=%(word)s">%(word)s</a>；</p>

<p>4. 您可以试着自己<a href="http://dj.iciba.com/v5/djadd.php">添加例句</a>。</p>

</body>
</html>
'''
