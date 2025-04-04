import request from "@/utils/request";

/**
 * 登录
 * @param data 登录的表单数据
 */
export const login = (data) => {
  return request.post("/rest/authenticate", data);
};

/**
 * 登出
 */
export const logout = () => {
  return request.post("/rest/logout");
};


/**
 * 获取个人信息
 */
export const getCurrentUser = () => {
  return request.get("/rest/users/current");
};

/**
 * 获取个人动态
 * @param {*} userId 用户ID
 */
export const getAccessLogsByUserId = (userId) => {
  return request.get("/rest/access/log", {
    params: {
      userId: userId,
      sortDesc: ["createTime"],
      pageSize: 5,
      resourceType: [0, 1, 2],
    },
  });
};

/**
 * 保存个人配置
 */
export const saveUserProfile = (data) => {
  return request.post("/rest/users/profile", data);
};

/**
 * 修改密码
 */
export const updatePassword = (data) => {
  return request.post("/rest/users/password", data);
};

//人员管理页面
export const showPersonList = (data) => {
  return request.post("/api/plan/showPersonList", data);
}

export const removeMember = (data) => {
  return request.post("/api/plan/removeMember", data);
}

export const modifyRole = (data) => {
  return request.post("/api/plan/modifyRole", data);
}

export const addMember = (data) => {
  return request.post("/api/plan/addMember", data);
}

export const showActivity = (data) => {
  return request.post("/api/plan/showActivity", data);
}

export const showContribute = (data) => {
  return request.post("/api/plan/showContribute", data);
}

//任务管理页面
export const showTaskList = (data) => {
  return request.post("/api/plan/showTaskList", data);
}

export const addTask = (data) => {
  return request.post("/api/plan/addTask", data);
}


export const removeTask = (data) => {
  return request.post("/api/plan/removeTask", data);
}

export const notice = (data) => {
  return request.post("/api/plan/notice", data);
}

export const addSubTask = (data) => {
  return request.post("/api/plan/addSubTask", data);
}

export const addReview = (data) => {
  return request.post("/api/plan/reviewTask", data);
}

export const getTaskReviews = (data) => {
  return request.post("/api/plan/getTaskReviews", data);
}

export const changeOrder = (data) => {
  return request.post("/api/plan/changeOrder", data);
}

export const modifyTaskContent = (data) => {
  return request.post("/api/plan/modifyTaskContent", data);
}

export const watchMyTask = (data) => {
  return request.post("/api/plan/watchMyTask", data);
}

export const completeTask = (data) => {
  return request.post("/api/plan/completeTask", data);
}

//项目管理页面
export const newProject = (data) => {
  return request.post("/api/plan/newProject", data);
}

export const watchAllProject = (data) => {
  return request.post("/api/plan/watchAllProject", data);
}

export const modifyProject = (data) => {
  return request.post("/api/plan/modifyProject", data);
}

export const deleteProject  = (data) => {
  return request.post("/api/plan/deleteProject", data);
}

export const modifyProjectStatus  = (data) => {
  return request.post("/api/plan/modifyProjectStatus", data);
}

export const getEmail = (data) => {
  return request.post("/api/plan/getEmail", data);
}


export const showNoticeList = (data) => {
  return request.post("/api/plan/showNoticeList", data);
}

export const removeNotice = (data) => {
  return request.post("/api/plan/removeNotice", data);
}

export const readNotice = (data) => {
  return request.post('api/plan/readNotice', data);
}

export const userDocList = (data) => {
  return request.post("/api/doc/userDocList", data);
}

export const userCollectDocList = (data) => {
  return request.post("/api/doc/userCollectDocList", data);
}

export const addDocToCollect = (data) => {
  return request.post("/api/doc/addDocToCollect", data);
}

export const delDocFromCollect = (data) => {
  return request.post("/api/doc/delDocFromCollect", data);
}

export const userCreateDoc = (data) => {
  return request.post("/api/doc/userCreateDoc", data);
}

export const userEditDocOther = (data) => {
  return request.post("/api/doc/userEditDocOther", data);
}

export const userDelDoc = (data) => {
  return request.post("/api/doc/userDelDoc", data);
}

export const docTimeUpdate = (data) => {
  return request.post("/api/doc/docTimeUpdate", data);
}

export const userEditDocContent = (data) => {
  return request.post("/api/doc/userEditDocContent", data);
}

export const userGetDocLock = (data) => {
  return request.post("/api/doc/userGetDocLock", data);
}


export const userReleaseDocLock = (data) => {
  return request.post("/api/doc/userReleaseDocLock", data);
}

export const isDocLocked = (data) => {
  return request.post("/api/doc/isDocLocked", data);
}

export const generateLabel = (data) => {
  return request.post("/api/ai/generateLabel", data);
}