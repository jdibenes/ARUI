
using System;
using System.Text;
using UnityEngine;

public class AARUI_HL2SS_IPC : MonoBehaviour
{
    uint m_userIntentComplete;

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        GetMessage();
    }

    #region Message Handling

    bool GetMessage()
    {
        uint command;
        byte[] data;
        if (!hl2ss.PullMessage(out command, out data)) { return false; }
        hl2ss.PushResult(ProcessMessage(command, data));
        hl2ss.AcknowledgeMessage(command);
        return true;
    }

    uint ProcessMessage(uint command, byte[] data)
    {
        uint ret = ~0U;

        switch (command)
        {
        case 0x00000000U: ret = MSG_Initialize(data); break;
        case 0x00000010U: ret = MSG_SetTasks(data); break;
        case 0x00000011U: ret = MSG_SetCurrentTaskID(data); break;
        case 0x00000012U: ret = MSG_SetTaskListActive(data); break;
        case 0x00000013U: ret = MSG_SetAllTasksDone(data); break;
        case 0x00000014U: ret = MSG_ToggleTaskList(data); break;
        case 0x00000015U: ret = MSG_SetTaskListEyeEventsActive(data); break;
        case 0x00000016U: ret = MSG_MuteAudio(data); break;
        case 0x00000020U: ret = MSG_GetUserFeedbackResult(data); break;
        case 0x00000021U: ret = MSG_TryGetUserFeedbackOnUserIntent(data); break;
        case 0x00000022U: ret = MSG_ShowSkipNotification(data); break;
        case 0xFFFFFFFFU: ret = MSG_Disconnect(data); break;
        }

        return ret;
    }

    void UserIntentCallback()
    {
        m_userIntentComplete = 1;
    }

    #endregion

    #region Message 

    uint MSG_Initialize(byte[] data)
    {
        AngelARUI.Instance.SetUserIntentCallback(UserIntentCallback);
        return 0;
    }

    uint MSG_SetTasks(byte[] data)
    {
        try
        {
            string tasks_block = Encoding.UTF8.GetString(data, 0, data.Length);

            string[] tasks_flat = tasks_block.Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries);
            if (tasks_flat.Length <= 0) { return 2; }

            string[,] tasks = new string[tasks_flat.Length, 2];

            for (int i = 0; i < tasks_flat.Length; ++i)
            {
                string task = tasks_flat[i];

                tasks[i, 0] = task.Substring(0, 1);
                tasks[i, 1] = task.Substring(1);
            }

            AngelARUI.Instance.SetTasks(tasks);
        }
        catch
        {
            return 1;
        }

        return 0;
    }

    uint MSG_SetCurrentTaskID(byte[] data)
    {
        try
        {
            int task_id = BitConverter.ToInt32(data, 0);
            AngelARUI.Instance.SetCurrentTaskID(task_id);
        }
        catch 
        {
            return 1;
        }
                
        return 0;
    }

    uint MSG_SetTaskListActive(byte[] data)
    {
        try
        {
            int enable = BitConverter.ToInt32(data, 0);
            AngelARUI.Instance.SetTaskListActive(enable != 0);
        }
        catch
        {
            return 1;
        }
        
        return 0;
    }

    uint MSG_SetAllTasksDone(byte[] data)
    {
        AngelARUI.Instance.SetAllTasksDone();
        return 0;
    }

    uint MSG_ToggleTaskList(byte[] data)
    {
        AngelARUI.Instance.ToggleTasklist();
        return 0;
    }

    uint MSG_SetTaskListEyeEventsActive(byte[] data)
    {
        try
        {
            int active = BitConverter.ToInt32(data, 0);
            AngelARUI.Instance.SetTasklistEyeEventsActive(active != 0);
        }
        catch
        {
            return 1;
        }

        return 0;
    }

    uint MSG_MuteAudio(byte[] data)
    {
        try
        {
            int mute = BitConverter.ToInt32(data, 0);
            AngelARUI.Instance.MuteAudio(mute != 0);
        }
        catch
        {
            return 1;
        }

        return 0;
    }

    uint MSG_GetUserFeedbackResult(byte[] data)
    {
        return m_userIntentComplete;
    }

    uint MSG_TryGetUserFeedbackOnUserIntent(byte[] data)
    {
        try
        {
            string msg = Encoding.UTF8.GetString(data, 0, data.Length);
            m_userIntentComplete = 0;
            AngelARUI.Instance.TryGetUserFeedbackOnUserIntent(msg);
        }
        catch
        {
            return 1;
        }

        return 0;
    }

    uint MSG_ShowSkipNotification(byte[] data)
    {
        try
        {
            int show = BitConverter.ToInt32(data, 0);
            AngelARUI.Instance.ShowSkipNotification(show != 0);
        }
        catch
        {
            return 1;
        }

        return 0;
    }

    uint MSG_Disconnect(byte[] data)
    {
        return ~0U;
    }

    #endregion
}
