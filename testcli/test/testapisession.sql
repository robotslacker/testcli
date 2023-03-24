_use api
-- 只有DEFAULT一列
_SESSION SHOW;

-- 保存当前会话
_SESSION SAVE mySession;
-- 重新查看时候应该为两列
_SESSION SHOW;

-- 设置HTTPS_VERIFY
SET HTTPS_VERIFY ON
-- 重新查看时应该被选择项的选项已经被设置
_SESSION SHOW;

-- RELEASE连接
_SESSION RELEASE;
-- 重新查看时应该只有默认连接
_SESSION SHOW;

-- 保存当前会话
_SESSION SAVE mySession2;
-- 设置HTTPS_VERIFY
SET PROXY http://127.0.0.1:8000
-- 重新查看时应该被选择项的选项已经被设置
_SESSION SHOW;

-- RELEASE连接
_SESSION RELEASE;
-- 重新查看时应该只有默认连接
_SESSION SHOW;
