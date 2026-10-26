-- University photographs: a public bucket for card images.
-- Reads are open through the public URL; writes are restricted to the
-- service role (the administrative uploader). The bucket-level upload
-- restrictions cap the object size and allowed image types.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'university-images',
  'university-images',
  true,
  4194304,
  array['image/jpeg', 'image/png', 'image/webp']
)
on conflict (id) do nothing;

create policy "university-images service role insert"
  on storage.objects
  for insert
  to service_role
  with check (bucket_id = 'university-images');

create policy "university-images service role update"
  on storage.objects
  for update
  to service_role
  using (bucket_id = 'university-images')
  with check (bucket_id = 'university-images');

create policy "university-images service role select"
  on storage.objects
  for select
  to service_role
  using (bucket_id = 'university-images');
