code_vk = '''   var service_key = "dc9c574ddc9c574ddc9c574d3edcf33578ddc9cdc9c574d82ad37576942a6ff567e7699";
                var all_groups = [], groups = [], count = 0;
                var offset = API.storage.get({"access_token": service_key, "key": "offset"});
                
                if (offset == '') {
                    offset = 0;
                } else {
                    offset = parseInt(offset);
                    }
                    
                var friends = API.friends.get({"user_id": Args.user_id, "count": 22, "offset": offset}).items;
                
                while (count < friends.length) {
                    groups =  API.groups.get({"user_id": friends[count]}).items;
                    if (groups.length > 0) {
                        all_groups = all_groups + groups;
                    }
                    count = count + 1;
                }
                
                var display_offset = offset;
                
                if (friends.length < 22) {
                    offset = 0;
                } else {
                    offset = offset + friends.length;
                }               
                API.storage.set({"access_token": service_key, "key": "offset", "value": offset});

                return [all_groups , display_offset + friends.length];'''
                
code_get_info = '''var d_info = API.users.get({"user_ids": Args.user_ids})[0];
                    var friends = API.friends.get({"user_id": d_info.id}).items;
                    var groups = API.groups.get({"user_id": d_info.id}).items;
                    var info = [];
                    if (d_info.id == null) {
                        return null;
                    } else {
                    info.id = d_info.id;
                    info.first_name = d_info.first_name;
                    info.last_name = d_info.last_name;
                    info.friends = friends;
                    info.groups = groups;
                    return info;
                    }
                '''
                
code_group_info =    '''var group = API.groups.getById({"group_ids": Args.group_ids, "fields": "members_count"});
                        var count = 0, group_info = [];
                        var group1 = group_info[0];
                       
                        while (count < group.length) {
                            var dict = {};
                            dict.id = group[count].id;
                            dict.name = group[count].name;
                            dict.members_count = group[count].members_count;
                            group_info.push(dict);
                            count = count + 1;
                        }
                        return group_info;
                    '''